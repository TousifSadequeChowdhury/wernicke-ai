"""
Wraps ChromaDB: a local, zero-config vector database.

Every chunk is stored with a session_id in its metadata, and every read
(query, list) or delete is filtered by that same session_id. This is
what keeps different visitors' documents completely separate from each
other in the live deployment.

Swapping this out for pgvector or Pinecone later only means rewriting
the functions in this file — main.py never talks to ChromaDB directly.
"""
from functools import lru_cache
from typing import List, Dict, Any
import uuid

from . import config
from .embeddings import embed_texts, embed_query

COLLECTION_NAME = "documents"


@lru_cache(maxsize=1)
def _get_collection():
    import chromadb

    client = chromadb.PersistentClient(
        path=str(config.CHROMA_DIR),
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(doc_id: str, doc_name: str, chunks: List[str], session_id: str) -> int:
    if not chunks:
        return 0

    collection = _get_collection()
    embeddings = embed_texts(chunks)
    ids = [f"{doc_id}::{i}" for i in range(len(chunks))]
    metadatas = [
        {"doc_id": doc_id, "doc_name": doc_name, "chunk_index": i, "session_id": session_id}
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    return len(chunks)


def query(text: str, session_id: str, top_k: int = 4) -> List[Dict[str, Any]]:
    collection = _get_collection()

    matching = collection.get(where={"session_id": session_id}, include=[])
    if not matching["ids"]:
        return []

    top_k = min(top_k, len(matching["ids"]))
    query_embedding = embed_query(text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"session_id": session_id},
        include=["documents", "metadatas", "distances"],
    )

    out = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for doc_text, meta, dist in zip(docs, metas, dists):
        similarity = 1 - dist
        out.append({
            "text": doc_text,
            "doc_id": meta["doc_id"],
            "doc_name": meta["doc_name"],
            "chunk_index": meta["chunk_index"],
            "score": round(float(similarity), 4),
        })
    return out


def list_documents(session_id: str) -> List[Dict[str, Any]]:
    collection = _get_collection()
    matching = collection.get(where={"session_id": session_id}, include=["metadatas"])

    seen: Dict[str, Dict[str, Any]] = {}
    for meta in matching["metadatas"]:
        doc_id = meta["doc_id"]
        if doc_id not in seen:
            seen[doc_id] = {"doc_id": doc_id, "doc_name": meta["doc_name"], "num_chunks": 0}
        seen[doc_id]["num_chunks"] += 1
    return list(seen.values())


def delete_document(doc_id: str, session_id: str) -> bool:
    collection = _get_collection()
    existing = collection.get(where={"$and": [{"doc_id": doc_id}, {"session_id": session_id}]})
    if not existing["ids"]:
        return False
    collection.delete(ids=existing["ids"])
    return True


def new_doc_id() -> str:
    return uuid.uuid4().hex[:12]

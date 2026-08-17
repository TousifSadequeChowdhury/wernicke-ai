"""Pydantic models describing API request/response shapes."""
from typing import List, Optional
from pydantic import BaseModel, Field


class SourceChunk(BaseModel):
    doc_id: str
    doc_name: str
    chunk_index: int
    text: str
    score: float


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    confidence: float
    low_confidence: bool
    possible_hallucination: bool
    latency_ms: float


class DocumentInfo(BaseModel):
    doc_id: str
    doc_name: str
    num_chunks: int


class UploadResponse(BaseModel):
    doc_id: str
    doc_name: str
    num_chunks: int
    message: str


class EvalStats(BaseModel):
    total_queries: int
    low_confidence_rate: float
    possible_hallucination_rate: float
    avg_latency_ms: float
    avg_confidence: float

"""
Pydantic models for RAG Orchestrator Service
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class Citation(BaseModel):
    """Citation for a source document"""
    file_id: str
    file_name: str
    source: str  # box, sharepoint, onedrive
    page_number: Optional[int] = None
    chunk_id: Optional[str] = None
    relevance_score: float = Field(ge=0.0, le=1.0)
    excerpt: str
    metadata: Dict[str, Any] = {}

class TableData(BaseModel):
    """Structured table data"""
    title: str
    headers: List[str]
    rows: List[List[str]]
    caption: Optional[str] = None
    source_documents: List[str] = []  # file IDs

class ChartData(BaseModel):
    """Chart visualization data"""
    title: str
    chart_type: str  # bar, line, pie, scatter, etc.
    data: Dict[str, Any]
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    caption: Optional[str] = None
    source_documents: List[str] = []  # file IDs

class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    tenant_id: str = "default"
    upn: str
    top_k: int = Field(default=8, ge=1, le=50)
    include_tables: bool = True
    include_charts: bool = True
    filters: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    """Query response model"""
    query: str
    answer: str
    citations: List[Citation]
    tables: List[TableData] = []
    charts: List[ChartData] = []
    metadata: Dict[str, Any] = {}
    processing_time_ms: int
    total_results: int
    security_trimmed: bool = False

class SearchResult(BaseModel):
    """Search result from Azure AI Search"""
    file_id: str
    file_name: str
    source: str
    content: str
    metadata: Dict[str, Any]
    score: float
    chunk_id: Optional[str] = None
    page_number: Optional[int] = None

class AIResponse(BaseModel):
    """AI-generated response"""
    answer: str
    citations: List[Citation]
    tables: List[TableData] = []
    charts: List[ChartData] = []
    processing_time_ms: int
    model_used: str
    tokens_used: int

class SecurityFilter(BaseModel):
    """Security filter for queries"""
    tenant_id: str
    upn: str
    filter_expression: str
    principals: List[str]
    groups: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class QueryLog(BaseModel):
    """Query log entry for audit"""
    timestamp: datetime
    tenant_id: str
    upn: str
    query: str
    answer: str
    citations: List[Dict[str, Any]]
    table_count: int
    chart_count: int
    security_trace: Dict[str, Any]
    processing_time_ms: int

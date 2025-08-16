from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
import json
import httpx
import pymongo
from datetime import datetime
import logging
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import openai
from .models import QueryRequest, QueryResponse, Citation, TableData, ChartData
from .search import AzureSearchService
from .ai import OpenAIService
from .security import SecurityService

app = FastAPI(title="RAG Orchestrator", version="1.0.0")
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize services
mongo_client = pymongo.MongoClient(os.getenv("MONGODB_URL"))
db = mongo_client.unstructured_data

search_service = AzureSearchService(
    endpoint=os.getenv("AZURE_AI_SEARCH_ENDPOINT"),
    key=os.getenv("AZURE_AI_SEARCH_KEY")
)

ai_service = OpenAIService(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    key=os.getenv("AZURE_OPENAI_KEY")
)

security_service = SecurityService(
    authz_url="http://authz:8083"
)

@app.get("/healthz")
def health_check():
    return {"status": "ok", "service": "orchestrator", "timestamp": datetime.utcnow().isoformat()}

@app.get("/query_secure")
async def query_secure(
    upn: str = Query(..., description="User Principal Name"),
    q: str = Query("", description="Query text"),
    tenant_id: str = Query("default", description="Tenant ID"),
    top_k: int = Query(8, description="Number of results to return"),
    include_tables: bool = Query(True, description="Include table generation"),
    include_charts: bool = Query(True, description="Include chart generation")
):
    """Security-trimmed query endpoint with comprehensive response processing"""
    
    try:
        # Step 1: Resolve user principals for security filtering
        security_filter = await security_service.build_filter(upn, tenant_id)
        
        # Step 2: Perform hybrid search with security filter
        search_results = await search_service.search(
            query=q,
            filter_expression=security_filter.filter_expression,
            top_k=top_k,
            tenant_id=tenant_id
        )
        
        # Step 3: Final security gate - verify access to each result
        verified_results = []
        for result in search_results:
            if await security_service.verify_access(upn, result.file_id, tenant_id):
                verified_results.append(result)
        
        # Step 4: Generate AI response with citations
        ai_response = await ai_service.generate_answer(
            query=q,
            context_documents=verified_results,
            include_tables=include_tables,
            include_charts=include_charts
        )
        
        # Step 5: Log the query and response for audit
        await log_query_response(
            upn=upn,
            tenant_id=tenant_id,
            query=q,
            response=ai_response,
            security_trace={
                "principals_used": security_filter.principals,
                "filter_applied": security_filter.filter_expression,
                "results_before_gate": len(search_results),
                "results_after_gate": len(verified_results)
            }
        )
        
        return QueryResponse(
            query=q,
            answer=ai_response.answer,
            citations=ai_response.citations,
            tables=ai_response.tables if include_tables else [],
            charts=ai_response.charts if include_charts else [],
            metadata={
                "total_results": len(verified_results),
                "processing_time_ms": ai_response.processing_time_ms,
                "security_trimmed": len(search_results) - len(verified_results) > 0
            }
        )
        
    except Exception as e:
        logger.error(f"Query failed for {upn}: {str(e)}")
        raise HTTPException(status_code=500, detail="Query processing failed")

@app.get("/query")
async def query_legacy(
    q: str = Query("", description="Query text"),
    tenant_id: str = Query("default", description="Tenant ID")
):
    """Legacy query endpoint without security trimming (for backward compatibility)"""
    
    # This endpoint should be deprecated in production
    # For now, route to secure endpoint with a default user
    return await query_secure(
        upn="system@internal.com",
        q=q,
        tenant_id=tenant_id
    )

async def log_query_response(
    upn: str,
    tenant_id: str,
    query: str,
    response: Any,
    security_trace: Dict[str, Any]
):
    """Log query and response for audit purposes"""
    
    log_entry = {
        "timestamp": datetime.utcnow(),
        "tenant_id": tenant_id,
        "upn": upn,
        "query": query,
        "answer": response.answer,
        "citations": [c.dict() for c in response.citations],
        "table_count": len(response.tables or []),
        "chart_count": len(response.charts or []),
        "security_trace": security_trace,
        "processing_time_ms": response.processing_time_ms
    }
    
    db.qa_logs.insert_one(log_entry)

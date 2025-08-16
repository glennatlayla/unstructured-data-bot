"""
Azure AI Search integration for RAG Orchestrator
"""

import os
import logging
from typing import List, Optional, Dict, Any
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from .models import SearchResult

logger = logging.getLogger(__name__)

class AzureSearchService:
    """Service for interacting with Azure AI Search"""
    
    def __init__(self, endpoint: str, key: str, index_name: str = "unstructured-data"):
        self.endpoint = endpoint
        self.key = key
        self.index_name = index_name
        self.client = None
        
        if endpoint and key:
            try:
                self.client = SearchClient(
                    endpoint=endpoint,
                    index_name=index_name,
                    credential=AzureKeyCredential(key)
                )
                logger.info(f"Azure Search client initialized for index: {index_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Search client: {e}")
                self.client = None
    
    async def search(
        self, 
        query: str, 
        filter_expression: Optional[str] = None,
        top_k: int = 8,
        tenant_id: Optional[str] = None,
        include_vectors: bool = False
    ) -> List[SearchResult]:
        """
        Perform semantic search with security filtering
        
        Args:
            query: Search query text
            filter_expression: Security filter expression
            top_k: Number of results to return
            tenant_id: Tenant ID for filtering
            include_vectors: Whether to include vector embeddings
            
        Returns:
            List of search results
        """
        if not self.client:
            logger.warning("Azure Search client not initialized")
            return []
        
        try:
            # Build search options
            search_options = {
                "top": top_k,
                "include_total_count": True,
                "query_type": "semantic",
                "query_language": "en-us",
                "semantic_configuration_name": "default"
            }
            
            # Add filters
            filters = []
            if tenant_id:
                filters.append(f"tenant_id eq '{tenant_id}'")
            if filter_expression:
                filters.append(filter_expression)
            
            if filters:
                search_options["filter"] = " and ".join(filters)
            
            # Add vector search if requested
            if include_vectors:
                search_options["vector_queries"] = [
                    {
                        "vector": self._get_query_embedding(query),
                        "k_nearest_neighbors": top_k,
                        "fields": "content_vector"
                    }
                ]
            
            # Perform search
            results = self.client.search(
                search_text=query,
                **search_options
            )
            
            # Convert to SearchResult objects
            search_results = []
            for result in results:
                search_result = SearchResult(
                    file_id=result.get("file_id", ""),
                    file_name=result.get("file_name", ""),
                    source=result.get("source", ""),
                    content=result.get("content", ""),
                    metadata=result.get("metadata", {}),
                    score=result.get("@search.score", 0.0),
                    chunk_id=result.get("chunk_id"),
                    page_number=result.get("page_number")
                )
                search_results.append(search_result)
            
            logger.info(f"Search returned {len(search_results)} results for query: {query}")
            return search_results
            
        except AzureError as e:
            logger.error(f"Azure Search error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            return []
    
    async def get_document(self, file_id: str, tenant_id: Optional[str] = None) -> Optional[SearchResult]:
        """Get a specific document by ID"""
        if not self.client:
            return None
        
        try:
            # Build filter
            filter_expr = f"file_id eq '{file_id}'"
            if tenant_id:
                filter_expr += f" and tenant_id eq '{tenant_id}'"
            
            results = self.client.search(
                search_text="",
                filter=filter_expr,
                top=1
            )
            
            for result in results:
                return SearchResult(
                    file_id=result.get("file_id", ""),
                    file_name=result.get("file_name", ""),
                    source=result.get("source", ""),
                    content=result.get("content", ""),
                    metadata=result.get("metadata", {}),
                    score=result.get("@search.score", 0.0),
                    chunk_id=result.get("chunk_id"),
                    page_number=result.get("page_number")
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document {file_id}: {e}")
            return None
    
    async def get_suggestions(self, query: str, tenant_id: Optional[str] = None) -> List[str]:
        """Get search suggestions for autocomplete"""
        if not self.client:
            return []
        
        try:
            suggestions = self.client.suggest(
                search_text=query,
                suggester_name="sg-suggestions",
                filter=f"tenant_id eq '{tenant_id}'" if tenant_id else None,
                top=5
            )
            
            return [suggestion.get("text", "") for suggestion in suggestions]
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """Get vector embedding for query (placeholder - would integrate with OpenAI)"""
        # This would call OpenAI's embedding API
        # For now, return a placeholder
        return [0.0] * 1536  # OpenAI ada-002 embedding dimension
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Azure Search service health"""
        try:
            if not self.client:
                return {
                    "status": "unavailable",
                    "error": "Client not initialized"
                }
            
            # Try a simple search to test connectivity
            results = self.client.search(
                search_text="test",
                top=1
            )
            
            # Consume the iterator to test
            list(results)
            
            return {
                "status": "healthy",
                "endpoint": self.endpoint,
                "index": self.index_name
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

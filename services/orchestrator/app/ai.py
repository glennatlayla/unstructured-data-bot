"""
OpenAI integration for RAG Orchestrator
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional
import openai
from openai import AzureOpenAI
from .models import SearchResult, AIResponse, Citation, TableData, ChartData

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI/Azure OpenAI integration"""
    
    def __init__(self, endpoint: str, key: str, api_version: str = "2024-02-15-preview"):
        self.endpoint = endpoint
        self.key = key
        self.api_version = api_version
        self.client = None
        
        if endpoint and key:
            try:
                self.client = AzureOpenAI(
                    azure_endpoint=endpoint,
                    api_key=key,
                    api_version=api_version
                )
                logger.info("Azure OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI client: {e}")
                self.client = None
    
    async def generate_answer(
        self,
        query: str,
        context_documents: List[SearchResult],
        include_tables: bool = True,
        include_charts: bool = True,
        model: str = "gpt-4"
    ) -> AIResponse:
        """
        Generate AI response with citations and optional structured data
        
        Args:
            query: User query
            context_documents: Retrieved search results
            include_tables: Whether to generate table data
            include_charts: Whether to generate chart data
            model: Model to use for generation
            
        Returns:
            AIResponse with answer, citations, and structured data
        """
        if not self.client:
            raise Exception("OpenAI client not initialized")
        
        start_time = time.time()
        
        try:
            # Build context from documents
            context = self._build_context(context_documents)
            
            # Build system prompt
            system_prompt = self._build_system_prompt(
                include_tables=include_tables,
                include_charts=include_charts
            )
            
            # Build user message
            user_message = self._build_user_message(
                query=query,
                context=context,
                include_tables=include_tables,
                include_charts=include_charts
            )
            
            # Generate response
            response = await self._call_openai(
                system_prompt=system_prompt,
                user_message=user_message,
                model=model
            )
            
            # Parse response
            ai_response = self._parse_ai_response(
                response=response,
                context_documents=context_documents,
                include_tables=include_tables,
                include_charts=include_charts
            )
            
            # Add timing and token info
            processing_time = int((time.time() - start_time) * 1000)
            ai_response.processing_time_ms = processing_time
            
            logger.info(f"Generated AI response in {processing_time}ms using {model}")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            raise
    
    async def generate_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Generate text embedding"""
        if not self.client:
            raise Exception("OpenAI client not initialized")
        
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def _build_context(self, documents: List[SearchResult]) -> str:
        """Build context string from search results"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            context_part = f"Document {i}:\n"
            context_part += f"File: {doc.file_name}\n"
            context_part += f"Source: {doc.source}\n"
            if doc.page_number:
                context_part += f"Page: {doc.page_number}\n"
            context_part += f"Content: {doc.content}\n"
            context_parts.append(context_part)
        
        return "\n---\n".join(context_parts)
    
    def _build_system_prompt(self, include_tables: bool, include_charts: bool) -> str:
        """Build system prompt for the AI model"""
        prompt = """You are an expert AI assistant that helps users find and understand information from their documents. 

Your task is to:
1. Answer the user's question based on the provided document context
2. Provide accurate citations for all information used
3. Generate helpful, actionable insights

Guidelines:
- Always base your answers on the provided documents
- Cite specific documents when making claims
- Be concise but comprehensive
- If information is not in the documents, say so clearly
- Use markdown formatting for better readability"""

        if include_tables:
            prompt += """

When appropriate, create structured tables to present information clearly. Tables should:
- Have descriptive titles
- Include relevant headers
- Present data in an organized format
- Include source document references"""

        if include_charts:
            prompt += """

When appropriate, suggest chart visualizations to help understand the data. Charts should:
- Have descriptive titles
- Use appropriate chart types (bar, line, pie, scatter, etc.)
- Include clear axis labels
- Provide insights about the data patterns"""

        prompt += """

Format your response as:
1. A clear answer to the question
2. Citations in [Document X] format
3. Tables (if applicable) in markdown format
4. Chart suggestions (if applicable) with data structure

Remember: Accuracy and proper citation are paramount."""
        
        return prompt
    
    def _build_user_message(
        self, 
        query: str, 
        context: str, 
        include_tables: bool, 
        include_charts: bool
    ) -> str:
        """Build user message for the AI model"""
        message = f"Question: {query}\n\n"
        message += "Context Documents:\n"
        message += context
        message += "\n\nPlease answer the question based on the provided documents."
        
        if include_tables:
            message += " If relevant, create tables to organize the information."
        
        if include_charts:
            message += " If relevant, suggest chart visualizations with the data structure."
        
        message += " Always cite your sources using [Document X] format."
        
        return message
    
    async def _call_openai(
        self, 
        system_prompt: str, 
        user_message: str, 
        model: str
    ) -> str:
        """Make OpenAI API call"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _parse_ai_response(
        self, 
        response: str, 
        context_documents: List[SearchResult],
        include_tables: bool,
        include_charts: bool
    ) -> AIResponse:
        """Parse AI response into structured format"""
        # Extract citations
        citations = self._extract_citations(response, context_documents)
        
        # Extract tables
        tables = []
        if include_tables:
            tables = self._extract_tables(response, context_documents)
        
        # Extract charts
        charts = []
        if include_charts:
            charts = self._extract_charts(response, context_documents)
        
        # Clean answer text
        answer = self._clean_answer_text(response)
        
        return AIResponse(
            answer=answer,
            citations=citations,
            tables=tables,
            charts=charts,
            processing_time_ms=0,  # Will be set by caller
            model_used="gpt-4",  # Will be updated with actual model
            tokens_used=0  # Would be extracted from OpenAI response
        )
    
    def _extract_citations(self, response: str, documents: List[SearchResult]) -> List[Citation]:
        """Extract citations from AI response"""
        citations = []
        
        # Look for [Document X] patterns
        import re
        doc_pattern = r'\[Document (\d+)\]'
        matches = re.findall(doc_pattern, response)
        
        for match in matches:
            doc_index = int(match) - 1  # Convert to 0-based index
            if 0 <= doc_index < len(documents):
                doc = documents[doc_index]
                citation = Citation(
                    file_id=doc.file_id,
                    file_name=doc.file_name,
                    source=doc.source,
                    page_number=doc.page_number,
                    chunk_id=doc.chunk_id,
                    relevance_score=doc.score,
                    excerpt=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    metadata=doc.metadata
                )
                citations.append(citation)
        
        return citations
    
    def _extract_tables(self, response: str, documents: List[SearchResult]) -> List[TableData]:
        """Extract table data from AI response"""
        tables = []
        
        # Look for markdown tables
        import re
        table_pattern = r'\|.*\|.*\n\|[\s\-:|]+\|\n(\|.*\|\n)*'
        table_matches = re.findall(table_pattern, response)
        
        for table_text in table_matches:
            # Parse table structure
            lines = table_text.strip().split('\n')
            if len(lines) >= 3:  # Header, separator, and at least one data row
                headers = [h.strip() for h in lines[0].split('|')[1:-1]]
                rows = []
                
                for line in lines[2:]:  # Skip header and separator
                    if line.strip() and '|' in line:
                        row = [cell.strip() for cell in line.split('|')[1:-1]]
                        if len(row) == len(headers):
                            rows.append(row)
                
                if headers and rows:
                    table = TableData(
                        title="Data Table",
                        headers=headers,
                        rows=rows,
                        source_documents=[doc.file_id for doc in documents]
                    )
                    tables.append(table)
        
        return tables
    
    def _extract_charts(self, response: str, documents: List[SearchResult]) -> List[ChartData]:
        """Extract chart data from AI response"""
        charts = []
        
        # Look for chart suggestions in the response
        # This is a simplified extraction - in practice, you might want more sophisticated parsing
        chart_keywords = ["chart", "graph", "visualization", "plot"]
        
        for keyword in chart_keywords:
            if keyword.lower() in response.lower():
                # Create a placeholder chart
                chart = ChartData(
                    title=f"Suggested {keyword.title()}",
                    chart_type="bar",  # Default type
                    data={"placeholder": "Chart data would be extracted here"},
                    source_documents=[doc.file_id for doc in documents]
                )
                charts.append(chart)
                break  # Just add one for now
        
        return charts
    
    def _clean_answer_text(self, response: str) -> str:
        """Clean the answer text by removing markdown and formatting"""
        # Remove markdown table formatting
        import re
        cleaned = re.sub(r'\|.*\|.*\n\|[\s\-:|]+\|\n(\|.*\|\n)*', '', response)
        
        # Remove extra whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        
        return cleaned.strip()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenAI service health"""
        try:
            if not self.client:
                return {
                    "status": "unavailable",
                    "error": "Client not initialized"
                }
            
            # Try a simple completion to test
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "endpoint": self.endpoint,
                "model_available": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

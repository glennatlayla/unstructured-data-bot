"""
Security service for RAG Orchestrator
"""

import httpx
import logging
from typing import Dict, Any, Optional
from .models import SecurityFilter

logger = logging.getLogger(__name__)

class SecurityService:
    """Service for security filtering and access control"""
    
    def __init__(self, authz_url: str):
        self.authz_url = authz_url
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def build_filter(self, upn: str, tenant_id: str) -> SecurityFilter:
        """
        Build security filter for Azure AI Search queries
        
        Args:
            upn: User Principal Name
            tenant_id: Tenant ID
            
        Returns:
            SecurityFilter with filter expression and principals
        """
        try:
            # Call AuthZ service to resolve principals
            response = await self.http_client.get(
                f"{self.authz_url}/filter",
                params={
                    "upn": upn,
                    "tenant_id": tenant_id,
                    "providers": ["box", "microsoft"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return SecurityFilter(**data)
            else:
                logger.error(f"AuthZ service returned {response.status_code}: {response.text}")
                # Return default filter that denies all access
                return SecurityFilter(
                    tenant_id=tenant_id,
                    upn=upn,
                    filter_expression="file_id eq 'none'",  # Deny all
                    principals=[],
                    groups=[]
                )
                
        except Exception as e:
            logger.error(f"Error building security filter: {e}")
            # Return restrictive filter on error
            return SecurityFilter(
                tenant_id=tenant_id,
                upn=upn,
                filter_expression="file_id eq 'none'",  # Deny all
                principals=[],
                groups=[]
            )
    
    async def verify_access(self, upn: str, file_id: str, tenant_id: str) -> bool:
        """
        Verify user has access to a specific file
        
        Args:
            upn: User Principal Name
            file_id: File ID to check
            tenant_id: Tenant ID
            
        Returns:
            True if user has access, False otherwise
        """
        try:
            # Call AuthZ service to verify access
            response = await self.http_client.post(
                f"{self.authz_url}/verify",
                json={
                    "upn": upn,
                    "file_id": file_id,
                    "tenant_id": tenant_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("has_access", False)
            else:
                logger.warning(f"AuthZ verify returned {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying access: {e}")
            return False
    
    async def get_user_principals(self, upn: str, tenant_id: str) -> Dict[str, Any]:
        """
        Get user principals and groups
        
        Args:
            upn: User Principal Name
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with principals and groups
        """
        try:
            response = await self.http_client.get(
                f"{self.authz_url}/resolve",
                params={
                    "upn": upn,
                    "tenant_id": tenant_id,
                    "providers": ["box", "microsoft"]
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"AuthZ resolve returned {response.status_code}: {response.text}")
                return {"principals": [], "groups": []}
                
        except Exception as e:
            logger.error(f"Error getting user principals: {e}")
            return {"principals": [], "groups": []}
    
    async def check_permission(
        self, 
        upn: str, 
        action: str, 
        resource: str, 
        tenant_id: str
    ) -> bool:
        """
        Check if user has permission for specific action on resource
        
        Args:
            upn: User Principal Name
            action: Action to perform (read, write, delete, etc.)
            resource: Resource identifier
            tenant_id: Tenant ID
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            response = await self.http_client.post(
                f"{self.authz_url}/check_permission",
                json={
                    "upn": upn,
                    "action": action,
                    "resource": resource,
                    "tenant_id": tenant_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("has_permission", False)
            else:
                logger.warning(f"AuthZ permission check returned {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    async def audit_access(
        self, 
        upn: str, 
        action: str, 
        resource: str, 
        tenant_id: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Audit access attempt
        
        Args:
            upn: User Principal Name
            action: Action attempted
            resource: Resource accessed
            tenant_id: Tenant ID
            success: Whether access was successful
            metadata: Additional metadata
        """
        try:
            await self.http_client.post(
                f"{self.authz_url}/audit",
                json={
                    "upn": upn,
                    "action": action,
                    "resource": resource,
                    "tenant_id": tenant_id,
                    "success": success,
                    "metadata": metadata or {},
                    "timestamp": "2025-01-27T00:00:00Z"  # Would use actual timestamp
                }
            )
        except Exception as e:
            logger.error(f"Error auditing access: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check security service health"""
        try:
            # Check AuthZ service health
            response = await self.http_client.get(f"{self.authz_url}/healthz")
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "authz_service": "available",
                    "authz_url": self.authz_url
                }
            else:
                return {
                    "status": "unhealthy",
                    "authz_service": "unavailable",
                    "error": f"AuthZ returned {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "authz_service": "unavailable",
                "error": str(e)
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()

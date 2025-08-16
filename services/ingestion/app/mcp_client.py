import asyncio
import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        self.logger = logger
        self.clients = {}
        self.base_urls = {
            "box": "http://mcp-box-server:8086",
            "sharepoint": "http://mcp-files-server:8087",
            "onedrive": "http://mcp-files-server:8087"
        }
        
    async def get_client(self, source: str) -> 'MCPClient':
        """Get MCP client for a specific source"""
        
        if source not in self.base_urls:
            raise ValueError(f"Unsupported source: {source}")
            
        if source not in self.clients:
            self.clients[source] = MCPClient()
            
        return self.clients[source]
    
    async def list_tools(self, source: str) -> List[Dict[str, Any]]:
        """List available tools from MCP server"""
        
        try:
            base_url = self.base_urls.get(source)
            if not base_url:
                raise ValueError(f"Unsupported source: {source}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/tools")
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to list tools from {source}: {str(e)}")
            return []
    
    async def call_tool(
        self, 
        source: str, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Call a specific tool on the MCP server"""
        
        try:
            base_url = self.base_urls.get(source)
            if not base_url:
                raise ValueError(f"Unsupported source: {source}")
            
            payload = {
                "name": tool_name,
                "arguments": arguments
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/tools/{tool_name}",
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name} on {source}: {str(e)}")
            return []
    
    async def list_folder(
        self, 
        source: str, 
        folder_id: str, 
        access_token: str
    ) -> List[Dict[str, Any]]:
        """List contents of a folder"""
        
        try:
            if source == "box":
                return await self._list_box_folder(folder_id, access_token)
            elif source in ["sharepoint", "onedrive"]:
                return await self._list_microsoft_folder(folder_id, access_token)
            else:
                raise ValueError(f"Unsupported source for folder listing: {source}")
                
        except Exception as e:
            logger.error(f"Failed to list folder {folder_id} from {source}: {str(e)}")
            return []
    
    async def _list_box_folder(self, folder_id: str, access_token: str) -> List[Dict[str, Any]]:
        """List Box folder contents"""
        
        try:
            arguments = {
                "folder_id": folder_id,
                "access_token": access_token
            }
            
            result = await self.call_tool("box", "list_folder", arguments)
            
            # Process Box-specific response format
            items = []
            for item in result:
                items.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "type": item.get("type"),
                    "size": item.get("size"),
                    "modified_at": item.get("modified_at"),
                    "created_at": item.get("created_at"),
                    "path": f"/{item.get('name')}"
                })
            
            return items
            
        except Exception as e:
            logger.error(f"Failed to list Box folder: {str(e)}")
            return []
    
    async def _list_microsoft_folder(self, folder_id: str, access_token: str) -> List[Dict[str, Any]]:
        """List Microsoft 365 folder contents"""
        
        try:
            arguments = {
                "drive_id": "root",  # Default to root drive
                "folder_id": folder_id,
                "access_token": access_token
            }
            
            result = await self.call_tool("sharepoint", "list_drive_items", arguments)
            
            # Process Microsoft-specific response format
            items = []
            for item in result:
                items.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "type": "folder" if item.get("folder") else "file",
                    "size": item.get("size"),
                    "modified_at": item.get("lastModifiedDateTime"),
                    "created_at": item.get("createdDateTime"),
                    "path": item.get("webUrl", "")
                })
            
            return items
            
        except Exception as e:
            logger.error(f"Failed to list Microsoft folder: {str(e)}")
            return []
    
    async def get_file_info(
        self, 
        source: str, 
        file_id: str, 
        access_token: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed file information"""
        
        try:
            if source == "box":
                return await self._get_box_file_info(file_id, access_token)
            elif source in ["sharepoint", "onedrive"]:
                return await self._get_microsoft_file_info(file_id, access_token)
            else:
                raise ValueError(f"Unsupported source for file info: {source}")
                
        except Exception as e:
            logger.error(f"Failed to get file info for {file_id} from {source}: {str(e)}")
            return None
    
    async def _get_box_file_info(self, file_id: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Get Box file information"""
        
        try:
            arguments = {
                "file_id": file_id,
                "access_token": access_token
            }
            
            result = await self.call_tool("box", "get_file_info", arguments)
            
            if result and len(result) > 0:
                file_info = result[0]
                return {
                    "id": file_info.get("id"),
                    "name": file_info.get("name"),
                    "size": file_info.get("size"),
                    "modified_at": file_info.get("modified_at"),
                    "created_at": file_info.get("created_at"),
                    "created_by": file_info.get("created_by"),
                    "modified_by": file_info.get("modified_by"),
                    "path": file_info.get("path"),
                    "etag": file_info.get("etag"),
                    "sha1": file_info.get("sha1")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get Box file info: {str(e)}")
            return None
    
    async def _get_microsoft_file_info(self, file_id: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Get Microsoft 365 file information"""
        
        try:
            arguments = {
                "drive_id": "root",
                "item_id": file_id,
                "access_token": access_token
            }
            
            result = await self.call_tool("sharepoint", "get_item_info", arguments)
            
            if result and len(result) > 0:
                file_info = result[0]
                return {
                    "id": file_info.get("id"),
                    "name": file_info.get("name"),
                    "size": file_info.get("size"),
                    "modified_at": file_info.get("lastModifiedDateTime"),
                    "created_at": file_info.get("createdDateTime"),
                    "created_by": file_info.get("createdBy", {}).get("user", {}).get("displayName"),
                    "modified_by": file_info.get("lastModifiedBy", {}).get("user", {}).get("displayName"),
                    "path": file_info.get("webUrl", ""),
                    "etag": file_info.get("eTag")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get Microsoft file info: {str(e)}")
            return None
    
    async def get_file_content(
        self, 
        source: str, 
        file_id: str, 
        access_token: str,
        max_bytes: int = 1000
    ) -> Optional[str]:
        """Get file content (limited for safety)"""
        
        try:
            if source == "box":
                return await self._get_box_file_content(file_id, access_token, max_bytes)
            elif source in ["sharepoint", "onedrive"]:
                return await self._get_microsoft_file_content(file_id, access_token, max_bytes)
            else:
                raise ValueError(f"Unsupported source for file content: {source}")
                
        except Exception as e:
            logger.error(f"Failed to get file content for {file_id} from {source}: {str(e)}")
            return None
    
    async def _get_box_file_content(self, file_id: str, access_token: str, max_bytes: int) -> Optional[str]:
        """Get Box file content"""
        
        try:
            arguments = {
                "file_id": file_id,
                "access_token": access_token
            }
            
            result = await self.call_tool("box", "get_file_content", arguments)
            
            if result and len(result) > 0:
                content = result[0].get("text", "")
                return content[:max_bytes] if len(content) > max_bytes else content
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get Box file content: {str(e)}")
            return None
    
    async def _get_microsoft_file_content(self, file_id: str, access_token: str, max_bytes: int) -> Optional[str]:
        """Get Microsoft 365 file content"""
        
        try:
            # For Microsoft files, we might need to download the file
            # This is a simplified implementation
            logger.info(f"Content download for Microsoft files not yet implemented")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get Microsoft file content: {str(e)}")
            return None
    
    async def get_permissions(
        self, 
        source: str, 
        item_id: str, 
        item_type: str, 
        access_token: str
    ) -> List[Dict[str, Any]]:
        """Get permissions for an item"""
        
        try:
            if source == "box":
                return await self._get_box_permissions(item_id, item_type, access_token)
            elif source in ["sharepoint", "onedrive"]:
                return await self._get_microsoft_permissions(item_id, access_token)
            else:
                raise ValueError(f"Unsupported source for permissions: {source}")
                
        except Exception as e:
            logger.error(f"Failed to get permissions for {item_id} from {source}: {str(e)}")
            return []
    
    async def _get_box_permissions(
        self, 
        item_id: str, 
        item_type: str, 
        access_token: str
    ) -> List[Dict[str, Any]]:
        """Get Box permissions"""
        
        try:
            arguments = {
                "item_id": item_id,
                "item_type": item_type,
                "access_token": access_token
            }
            
            result = await self.call_tool("box", "get_collaborations", arguments)
            
            if result and len(result) > 0:
                permissions = result[0].get("text", "[]")
                try:
                    return json.loads(permissions)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse Box permissions JSON")
                    return []
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get Box permissions: {str(e)}")
            return []
    
    async def _get_microsoft_permissions(self, item_id: str, access_token: str) -> List[Dict[str, Any]]:
        """Get Microsoft 365 permissions"""
        
        try:
            arguments = {
                "drive_id": "root",
                "item_id": item_id,
                "access_token": access_token
            }
            
            result = await self.call_tool("sharepoint", "get_permissions", arguments)
            
            if result and len(result) > 0:
                permissions = result[0].get("text", "[]")
                try:
                    return json.loads(permissions)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse Microsoft permissions JSON")
                    return []
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get Microsoft permissions: {str(e)}")
            return []
    
    async def health_check(self, source: str) -> bool:
        """Check health of MCP server"""
        
        try:
            base_url = self.base_urls.get(source)
            if not base_url:
                return False
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/healthz", timeout=5.0)
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Health check failed for {source}: {str(e)}")
            return False
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers"""
        
        status = {}
        
        for source in self.base_urls:
            try:
                is_healthy = await self.health_check(source)
                status[source] = {
                    "healthy": is_healthy,
                    "base_url": self.base_urls[source],
                    "checked_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                status[source] = {
                    "healthy": False,
                    "error": str(e),
                    "base_url": self.base_urls[source],
                    "checked_at": datetime.utcnow().isoformat()
                }
        
        return status

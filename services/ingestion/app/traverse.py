import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class DirectoryTraverser:
    def __init__(self, db, redis_client):
        self.db = db
        self.redis_client = redis_client
        
    async def traverse(
        self,
        tenant_id: str,
        source: str,
        mcp_client: Any,
        mode: str = "incremental",
        target_paths: Optional[List[str]] = None
    ):
        """Traverse directory structure and capture file metadata"""
        
        try:
            logger.info(f"Starting {mode} traversal for {tenant_id}/{source}")
            
            if mode == "full":
                await self._full_traversal(tenant_id, source, mcp_client)
            else:
                await self._incremental_traversal(tenant_id, source, mcp_client, target_paths)
                
            logger.info(f"Completed {mode} traversal for {tenant_id}/{source}")
            
        except Exception as e:
            logger.error(f"Traversal failed for {tenant_id}/{source}: {str(e)}")
            raise
    
    async def _full_traversal(self, tenant_id: str, source: str, mcp_client: Any):
        """Perform full directory traversal"""
        
        # Get root directory from MCP client
        root_items = await mcp_client.list_tools()
        
        # Process each root item
        for item in root_items:
            await self._process_item(tenant_id, source, item, mcp_client, depth=0)
    
    async def _incremental_traversal(
        self, 
        tenant_id: str, 
        source: str, 
        mcp_client: Any, 
        target_paths: Optional[List[str]] = None
    ):
        """Perform incremental traversal of specific paths"""
        
        if target_paths:
            # Process only specified paths
            for path in target_paths:
                await self._process_path(tenant_id, source, path, mcp_client)
        else:
            # Process paths that have changed since last scan
            changed_paths = await self._get_changed_paths(tenant_id, source)
            for path in changed_paths:
                await self._process_path(tenant_id, source, path, mcp_client)
    
    async def _process_item(
        self, 
        tenant_id: str, 
        source: str, 
        item: Dict[str, Any], 
        mcp_client: Any, 
        depth: int = 0
    ):
        """Process a single directory item"""
        
        try:
            # Extract item metadata
            item_metadata = {
                "file_id": item.get("id"),
                "tenant_id": tenant_id,
                "source": source,
                "name": item.get("name"),
                "path": item.get("path", ""),
                "size": item.get("size", 0),
                "mime_type": self._get_mime_type(item),
                "created_at": item.get("created_at"),
                "modified_at": item.get("modified_at"),
                "is_folder": item.get("type") == "folder",
                "depth": depth,
                "traversed_at": datetime.utcnow()
            }
            
            # Check if item already exists
            existing = self.db.files.find_one({
                "file_id": item_metadata["file_id"],
                "tenant_id": tenant_id
            })
            
            if existing:
                # Update existing record
                await self._update_item(tenant_id, item_metadata)
            else:
                # Create new record
                await self._create_item(tenant_id, item_metadata)
            
            # If it's a folder, traverse recursively
            if item_metadata["is_folder"] and depth < 10:  # Prevent infinite recursion
                await self._traverse_folder(tenant_id, source, item, mcp_client, depth + 1)
                
        except Exception as e:
            logger.error(f"Failed to process item {item.get('id')}: {str(e)}")
    
    async def _process_path(self, tenant_id: str, source: str, path: str, mcp_client: Any):
        """Process a specific path"""
        
        try:
            # Get path info from MCP client
            path_info = await mcp_client.get_item_info(path)
            await self._process_item(tenant_id, source, path_info, mcp_client)
            
        except Exception as e:
            logger.error(f"Failed to process path {path}: {str(e)}")
    
    async def _traverse_folder(
        self, 
        tenant_id: str, 
        source: str, 
        folder_item: Dict[str, Any], 
        mcp_client: Any, 
        depth: int
    ):
        """Recursively traverse a folder"""
        
        try:
            # Get folder contents
            folder_contents = await mcp_client.list_folder(folder_item["id"])
            
            # Process each item in the folder
            for item in folder_contents:
                await self._process_item(tenant_id, source, item, mcp_client, depth)
                
        except Exception as e:
            logger.error(f"Failed to traverse folder {folder_item['id']}: {str(e)}")
    
    async def _create_item(self, tenant_id: str, metadata: Dict[str, Any]):
        """Create a new file record"""
        
        try:
            # Generate content hash if available
            if metadata.get("size", 0) > 0:
                metadata["content_hash"] = self._generate_content_hash(metadata)
            
            # Set processing state
            metadata["processing_state"] = "pending"
            metadata["processing_stages"] = ["traversal_complete"]
            
            # Insert into database
            result = self.db.files.insert_one(metadata)
            logger.info(f"Created file record: {result.inserted_id}")
            
        except Exception as e:
            logger.error(f"Failed to create file record: {str(e)}")
            raise
    
    async def _update_item(self, tenant_id: str, metadata: Dict[str, Any]):
        """Update an existing file record"""
        
        try:
            # Update metadata
            update_data = {
                "modified_at": metadata["modified_at"],
                "size": metadata["size"],
                "traversed_at": metadata["traversed_at"],
                "processing_stages": ["traversal_updated"]
            }
            
            # Update in database
            result = self.db.files.update_one(
                {"file_id": metadata["file_id"], "tenant_id": tenant_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated file record: {metadata['file_id']}")
                
        except Exception as e:
            logger.error(f"Failed to update file record: {str(e)}")
            raise
    
    async def _get_changed_paths(self, tenant_id: str, source: str) -> List[str]:
        """Get paths that have changed since last scan"""
        
        try:
            # Query for files that have been modified since last scan
            last_scan = self.db.processing_state.find_one(
                {"tenant_id": tenant_id, "source": source},
                sort=[("last_success_ts", -1)]
            )
            
            if not last_scan:
                return []
            
            # Get files modified since last scan
            changed_files = self.db.files.find({
                "tenant_id": tenant_id,
                "source": source,
                "modified_at": {"$gt": last_scan["last_success_ts"]}
            })
            
            return [f["path"] for f in changed_files]
            
        except Exception as e:
            logger.error(f"Failed to get changed paths: {str(e)}")
            return []
    
    def _get_mime_type(self, item: Dict[str, Any]) -> str:
        """Determine MIME type from item"""
        
        if item.get("type") == "folder":
            return "application/x-directory"
        
        # Try to determine from file extension
        name = item.get("name", "")
        if name.endswith(".pdf"):
            return "application/pdf"
        elif name.endswith(".docx"):
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif name.endswith(".txt"):
            return "text/plain"
        elif name.endswith(".md"):
            return "text/markdown"
        else:
            return "application/octet-stream"
    
    def _generate_content_hash(self, metadata: Dict[str, Any]) -> str:
        """Generate content hash for file"""
        
        # Create hash from metadata
        hash_input = f"{metadata['file_id']}{metadata['size']}{metadata['modified_at']}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

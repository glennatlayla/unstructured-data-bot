import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ACLCapture:
    def __init__(self):
        self.logger = logger
        
    async def capture_permissions(
        self, 
        tenant_id: str, 
        source: str, 
        item_id: str, 
        permissions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Capture and store access control permissions for an item"""
        
        try:
            logger.info(f"Capturing permissions for {tenant_id}/{source}/{item_id}")
            
            # Process permissions
            processed_permissions = []
            for permission in permissions:
                processed_perm = self._process_permission(permission, source)
                if processed_perm:
                    processed_permissions.append(processed_perm)
            
            # Create permission record
            permission_record = {
                "tenant_id": tenant_id,
                "source": source,
                "item_id": item_id,
                "captured_at": datetime.utcnow(),
                "permissions": processed_permissions,
                "permission_count": len(processed_permissions),
                "source_metadata": {
                    "source_type": source,
                    "capture_method": "mcp_client"
                }
            }
            
            return permission_record
            
        except Exception as e:
            logger.error(f"Failed to capture permissions for {item_id}: {str(e)}")
            raise
    
    def _process_permission(self, permission: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
        """Process a single permission entry based on source type"""
        
        try:
            if source == "box":
                return self._process_box_permission(permission)
            elif source in ["sharepoint", "onedrive"]:
                return self._process_microsoft_permission(permission)
            else:
                logger.warning(f"Unknown source type for permission processing: {source}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to process permission: {str(e)}")
            return None
    
    def _process_box_permission(self, permission: Dict[str, Any]) -> Dict[str, Any]:
        """Process Box-specific permission format"""
        
        try:
            return {
                "permission_id": permission.get("id"),
                "accessible_by": {
                    "id": permission.get("accessible_by", {}).get("id"),
                    "name": permission.get("accessible_by", {}).get("name"),
                    "login": permission.get("accessible_by", {}).get("login"),
                    "type": permission.get("accessible_by", {}).get("type")
                },
                "role": permission.get("role"),
                "status": permission.get("status"),
                "permissions": {
                    "can_download": permission.get("permissions", {}).get("can_download", False),
                    "can_preview": permission.get("permissions", {}).get("can_preview", False),
                    "can_edit": permission.get("permissions", {}).get("can_edit", False),
                    "can_delete": permission.get("permissions", {}).get("can_delete", False),
                    "can_upload": permission.get("permissions", {}).get("can_upload", False),
                    "can_comment": permission.get("permissions", {}).get("can_comment", False)
                },
                "expires_at": permission.get("expires_at"),
                "created_at": permission.get("created_at"),
                "modified_at": permission.get("modified_at")
            }
            
        except Exception as e:
            logger.error(f"Failed to process Box permission: {str(e)}")
            return {}
    
    def _process_microsoft_permission(self, permission: Dict[str, Any]) -> Dict[str, Any]:
        """Process Microsoft 365 permission format"""
        
        try:
            return {
                "permission_id": permission.get("id"),
                "granted_to": {
                    "user": {
                        "id": permission.get("grantedTo", {}).get("user", {}).get("id"),
                        "displayName": permission.get("grantedTo", {}).get("user", {}).get("displayName"),
                        "email": permission.get("grantedTo", {}).get("user", {}).get("mail")
                    } if permission.get("grantedTo", {}).get("user") else None,
                    "application": permission.get("grantedTo", {}).get("application"),
                    "device": permission.get("grantedTo", {}).get("device")
                },
                "roles": permission.get("roles", []),
                "link": {
                    "type": permission.get("link", {}).get("type"),
                    "scope": permission.get("link", {}).get("scope"),
                    "webUrl": permission.get("link", {}).get("webUrl")
                } if permission.get("link") else None,
                "expirationDateTime": permission.get("expirationDateTime"),
                "hasPassword": permission.get("hasPassword", False),
                "password": permission.get("password")
            }
            
        except Exception as e:
            logger.error(f"Failed to process Microsoft permission: {str(e)}")
            return {}
    
    async def store_permissions(
        self, 
        db, 
        permission_record: Dict[str, Any]
    ) -> str:
        """Store permission record in database"""
        
        try:
            # Check if permissions already exist for this item
            existing = await db.permissions.find_one({
                "tenant_id": permission_record["tenant_id"],
                "source": permission_record["source"],
                "item_id": permission_record["item_id"]
            })
            
            if existing:
                # Update existing record
                result = await db.permissions.update_one(
                    {
                        "tenant_id": permission_record["tenant_id"],
                        "source": permission_record["source"],
                        "item_id": permission_record["item_id"]
                    },
                    {
                        "$set": {
                            "permissions": permission_record["permissions"],
                            "permission_count": permission_record["permission_count"],
                            "captured_at": permission_record["captured_at"],
                            "source_metadata": permission_record["source_metadata"]
                        }
                    }
                )
                logger.info(f"Updated permissions for {permission_record['item_id']}")
                return existing["_id"]
            else:
                # Insert new record
                result = await db.permissions.insert_one(permission_record)
                logger.info(f"Stored new permissions for {permission_record['item_id']}")
                return str(result.inserted_id)
                
        except Exception as e:
            logger.error(f"Failed to store permissions: {str(e)}")
            raise
    
    async def get_item_permissions(
        self, 
        db, 
        tenant_id: str, 
        source: str, 
        item_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve permissions for a specific item"""
        
        try:
            permission_record = await db.permissions.find_one({
                "tenant_id": tenant_id,
                "source": source,
                "item_id": item_id
            })
            
            return permission_record
            
        except Exception as e:
            logger.error(f"Failed to get item permissions: {str(e)}")
            return None
    
    async def get_user_permissions(
        self, 
        db, 
        tenant_id: str, 
        user_identifier: str, 
        source: str = None
    ) -> List[Dict[str, Any]]:
        """Get all permissions for a specific user across items"""
        
        try:
            query = {
                "tenant_id": tenant_id
            }
            
            if source:
                query["source"] = source
            
            # Search for user in permissions
            cursor = db.permissions.find(query)
            
            user_permissions = []
            async for doc in cursor:
                for permission in doc.get("permissions", []):
                    if self._is_user_in_permission(permission, user_identifier):
                        user_permissions.append({
                            "item_id": doc["item_id"],
                            "source": doc["source"],
                            "permission": permission,
                            "captured_at": doc["captured_at"]
                        })
            
            return user_permissions
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {str(e)}")
            return []
    
    def _is_user_in_permission(self, permission: Dict[str, Any], user_identifier: str) -> bool:
        """Check if a user is included in a permission entry"""
        
        # Check various user identifier fields
        user_fields = [
            permission.get("accessible_by", {}).get("id"),
            permission.get("accessible_by", {}).get("login"),
            permission.get("accessible_by", {}).get("email"),
            permission.get("granted_to", {}).get("user", {}).get("id"),
            permission.get("granted_to", {}).get("user", {}).get("email")
        ]
        
        return user_identifier in [field for field in user_fields if field]
    
    async def analyze_permission_patterns(
        self, 
        db, 
        tenant_id: str, 
        source: str = None
    ) -> Dict[str, Any]:
        """Analyze permission patterns for security insights"""
        
        try:
            pipeline = [
                {"$match": {"tenant_id": tenant_id}},
                {"$unwind": "$permissions"},
                {"$group": {
                    "_id": {
                        "role": "$permissions.role",
                        "source": "$source"
                    },
                    "count": {"$sum": 1}
                }}
            ]
            
            if source:
                pipeline[0]["$match"]["source"] = source
            
            results = list(db.permissions.aggregate(pipeline))
            
            # Process results
            patterns = {}
            for result in results:
                role = result["_id"]["role"]
                source = result["_id"]["source"]
                count = result["count"]
                
                if role not in patterns:
                    patterns[role] = {}
                
                patterns[role][source] = count
            
            return {
                "tenant_id": tenant_id,
                "source": source,
                "analyzed_at": datetime.utcnow(),
                "patterns": patterns
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze permission patterns: {str(e)}")
            return {}

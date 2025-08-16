import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)

class ChangeDetector:
    def __init__(self, db):
        self.db = db
        
    async def detect_changes(
        self, 
        tenant_id: str, 
        source: str, 
        current_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect changes between current and stored items"""
        
        try:
            logger.info(f"Detecting changes for {tenant_id}/{source}")
            
            # Get stored items from database
            stored_items = await self._get_stored_items(tenant_id, source)
            
            # Detect changes
            changes = {
                "added": [],
                "modified": [],
                "deleted": [],
                "unchanged": []
            }
            
            # Track processed items
            processed_ids = set()
            
            # Check current items against stored
            for current_item in current_items:
                item_id = current_item.get("id")
                if not item_id:
                    continue
                    
                processed_ids.add(item_id)
                stored_item = stored_items.get(item_id)
                
                if not stored_item:
                    # New item
                    changes["added"].append(current_item)
                else:
                    # Check if modified
                    if self._is_item_modified(current_item, stored_item):
                        changes["modified"].append(current_item)
                    else:
                        changes["unchanged"].append(current_item)
            
            # Find deleted items
            for stored_id in stored_items:
                if stored_id not in processed_ids:
                    changes["deleted"].append(stored_items[stored_id])
            
            # Log change summary
            logger.info(f"Change detection complete for {tenant_id}/{source}: "
                       f"{len(changes['added'])} added, "
                       f"{len(changes['modified'])} modified, "
                       f"{len(changes['deleted'])} deleted")
            
            return changes
            
        except Exception as e:
            logger.error(f"Change detection failed for {tenant_id}/{source}: {str(e)}")
            raise
    
    async def _get_stored_items(self, tenant_id: str, source: str) -> Dict[str, Any]:
        """Get stored items from database"""
        
        try:
            cursor = self.db.files.find({
                "tenant_id": tenant_id,
                "source": source
            })
            
            stored_items = {}
            async for doc in cursor:
                stored_items[doc["file_id"]] = doc
                
            return stored_items
            
        except Exception as e:
            logger.error(f"Failed to get stored items: {str(e)}")
            return {}
    
    def _is_item_modified(self, current_item: Dict[str, Any], stored_item: Dict[str, Any]) -> bool:
        """Check if an item has been modified"""
        
        # Check modification timestamp
        current_modified = current_item.get("modified_at")
        stored_modified = stored_item.get("modified_at")
        
        if current_modified != stored_modified:
            return True
        
        # Check file size
        current_size = current_item.get("size", 0)
        stored_size = stored_item.get("size", 0)
        
        if current_size != stored_size:
            return True
        
        # Check content hash if available
        current_hash = current_item.get("content_hash")
        stored_hash = stored_item.get("content_hash")
        
        if current_hash and stored_hash and current_hash != stored_hash:
            return True
        
        # Check ETag if available
        current_etag = current_item.get("etag")
        stored_etag = stored_item.get("etag")
        
        if current_etag and stored_etag and current_etag != stored_etag:
            return True
        
        return False
    
    async def track_change_history(
        self, 
        tenant_id: str, 
        source: str, 
        changes: Dict[str, Any]
    ):
        """Track change history for audit purposes"""
        
        try:
            change_record = {
                "tenant_id": tenant_id,
                "source": source,
                "timestamp": datetime.utcnow(),
                "change_summary": {
                    "added_count": len(changes["added"]),
                    "modified_count": len(changes["modified"]),
                    "deleted_count": len(changes["deleted"]),
                    "unchanged_count": len(changes["unchanged"])
                },
                "changes": changes
            }
            
            # Store change record
            await self.db.change_history.insert_one(change_record)
            
            logger.info(f"Change history recorded for {tenant_id}/{source}")
            
        except Exception as e:
            logger.error(f"Failed to track change history: {str(e)}")
    
    async def get_change_summary(
        self, 
        tenant_id: str, 
        source: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get change summary for a time period"""
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "tenant_id": tenant_id,
                        "source": source,
                        "timestamp": {"$gte": cutoff_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_changes": {"$sum": 1},
                        "total_added": {"$sum": "$change_summary.added_count"},
                        "total_modified": {"$sum": "$change_summary.modified_count"},
                        "total_deleted": {"$sum": "$change_summary.deleted_count"},
                        "last_change": {"$max": "$timestamp"}
                    }
                }
            ]
            
            result = list(self.db.change_history.aggregate(pipeline))
            
            if result:
                summary = result[0]
                return {
                    "tenant_id": tenant_id,
                    "source": source,
                    "period_days": days,
                    "total_changes": summary["total_changes"],
                    "total_added": summary["total_added"],
                    "total_modified": summary["total_modified"],
                    "total_deleted": summary["total_deleted"],
                    "last_change": summary["last_change"]
                }
            else:
                return {
                    "tenant_id": tenant_id,
                    "source": source,
                    "period_days": days,
                    "total_changes": 0,
                    "total_added": 0,
                    "total_modified": 0,
                    "total_deleted": 0,
                    "last_change": None
                }
                
        except Exception as e:
            logger.error(f"Failed to get change summary: {str(e)}")
            return {}
    
    async def cleanup_old_records(self, days_to_keep: int = 90):
        """Clean up old change history records"""
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            result = await self.db.change_history.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            logger.info(f"Cleaned up {result.deleted_count} old change records")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {str(e)}")

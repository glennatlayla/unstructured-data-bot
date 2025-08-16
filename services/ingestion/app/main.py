from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import pymongo
import redis
from datetime import datetime
import logging
from .traverse import DirectoryTraverser
from .change_detection import ChangeDetector
from .acl_capture import ACLCapture
from .mcp_client import MCPClient

app = FastAPI(title="Ingestion Service", version="1.0.0")
logger = logging.getLogger(__name__)

# Database connections
mongo_client = pymongo.MongoClient(os.getenv("MONGODB_URL"))
db = mongo_client.unstructured_data
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

# Initialize components
traverser = DirectoryTraverser(db, redis_client)
change_detector = ChangeDetector(db)
acl_capture = ACLCapture()
mcp_client = MCPClient()

class TraversalRequest(BaseModel):
    tenant_id: str
    source: str  # box, sharepoint, onedrive
    mode: str = "incremental"  # full, incremental
    paths: Optional[List[str]] = None

@app.get("/healthz")
def health_check():
    return {"status": "ok", "service": "ingestion", "timestamp": datetime.utcnow().isoformat()}

@app.post("/start")
async def start_ingestion(request: TraversalRequest, background_tasks: BackgroundTasks):
    """Start directory traversal and ingestion process"""
    
    try:
        # Validate tenant and source
        if request.source not in ["box", "sharepoint", "onedrive"]:
            raise HTTPException(status_code=400, detail="Invalid source")
        
        # Start background traversal
        background_tasks.add_task(
            run_traversal,
            request.tenant_id,
            request.source,
            request.mode,
            request.paths
        )
        
        return {
            "status": "started",
            "tenant_id": request.tenant_id,
            "source": request.source,
            "mode": request.mode,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to start ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start ingestion")

@app.post("/stop")
async def stop_ingestion(tenant_id: str, source: str):
    """Stop ongoing ingestion process"""
    
    # Implementation would cancel running tasks
    return {
        "status": "stopped",
        "tenant_id": tenant_id,
        "source": source,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/rescan")
async def rescan_paths(
    tenant_id: str,
    source: str,
    paths: List[str],
    background_tasks: BackgroundTasks
):
    """Rescan specific paths for changes"""
    
    background_tasks.add_task(
        run_targeted_scan,
        tenant_id,
        source,
        paths
    )
    
    return {
        "status": "rescan_started",
        "tenant_id": tenant_id,
        "source": source,
        "paths": paths,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/status")
async def get_status(tenant_id: str, source: str):
    """Get ingestion status for tenant and source"""
    
    # Query processing state from database
    status = db.processing_state.find({
        "tenant_id": tenant_id,
        "source": source
    }).sort("last_success_ts", -1).limit(10)
    
    return {
        "tenant_id": tenant_id,
        "source": source,
        "recent_activity": list(status),
        "timestamp": datetime.utcnow().isoformat()
    }

async def run_traversal(tenant_id: str, source: str, mode: str, paths: Optional[List[str]]):
    """Background task to run directory traversal"""
    
    try:
        logger.info(f"Starting {mode} traversal for {tenant_id}/{source}")
        
        # Get MCP client for the source
        mcp = await mcp_client.get_client(source)
        
        # Run traversal
        await traverser.traverse(
            tenant_id=tenant_id,
            source=source,
            mcp_client=mcp,
            mode=mode,
            target_paths=paths
        )
        
        logger.info(f"Completed traversal for {tenant_id}/{source}")
        
    except Exception as e:
        logger.error(f"Traversal failed for {tenant_id}/{source}: {str(e)}")

async def run_targeted_scan(tenant_id: str, source: str, paths: List[str]):
    """Background task for targeted path rescanning"""
    
    try:
        logger.info(f"Starting targeted scan for {tenant_id}/{source}: {paths}")
        
        # Implementation would rescan specific paths
        # and detect changes
        
        logger.info(f"Completed targeted scan for {tenant_id}/{source}")
        
    except Exception as e:
        logger.error(f"Targeted scan failed: {str(e)}")

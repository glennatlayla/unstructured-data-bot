from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import json
from typing import Dict, List, Any, Optional
from boxsdk import Client, OAuth2
import httpx

app = FastAPI(title="Box MCP Server", version="1.0.0")

# Initialize Box client
client_id = os.getenv("BOX_CLIENT_ID")
client_secret = os.getenv("BOX_CLIENT_SECRET")

class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

@app.get("/healthz")
async def health_check():
    return JSONResponse(
        content={
            "status": "ok",
            "service": "mcp-box-server",
            "version": "1.0.0"
        },
        status_code=200
    )

@app.get("/")
async def root():
    return {"message": "Box MCP Server"}

@app.get("/tools")
async def list_tools():
    """List available tools from Box MCP server"""
    tools = [
        {
            "name": "list_folder",
            "description": "List contents of a Box folder",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "folder_id": {"type": "string", "description": "Box folder ID"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["folder_id", "access_token"]
            }
        },
        {
            "name": "get_file_info",
            "description": "Get detailed file information from Box",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Box file ID"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["file_id", "access_token"]
            }
        },
        {
            "name": "get_file_content",
            "description": "Download file content from Box",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Box file ID"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["file_id", "access_token"]
            }
        },
        {
            "name": "get_collaborations",
            "description": "Get file/folder collaborations and permissions",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "description": "Box item ID"},
                    "item_type": {"type": "string", "enum": ["file", "folder"]},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["item_id", "item_type", "access_token"]
            }
        }
    ]
    return tools

@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolCallRequest):
    """Call a specific tool on the Box MCP server"""
    try:
        if tool_name == "list_folder":
            return await list_folder(request.arguments["folder_id"], request.arguments["access_token"])
        elif tool_name == "get_file_info":
            return await get_file_info(request.arguments["file_id"], request.arguments["access_token"])
        elif tool_name == "get_file_content":
            return await get_file_content(request.arguments["file_id"], request.arguments["access_token"])
        elif tool_name == "get_collaborations":
            return await get_collaborations(
                request.arguments["item_id"], 
                request.arguments["item_type"], 
                request.arguments["access_token"]
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

async def list_folder(folder_id: str, access_token: str) -> List[Dict[str, Any]]:
    """List contents of a Box folder"""
    try:
        # Initialize Box client with user token
        oauth = OAuth2(client_id=client_id, client_secret=client_secret, access_token=access_token)
        client = Client(oauth)
        
        folder = client.folder(folder_id)
        items = folder.get_items()
        
        result = []
        for item in items:
            result.append({
                "id": item.id,
                "name": item.name,
                "type": item.type,
                "size": getattr(item, "size", None),
                "modified_at": getattr(item, "modified_at", None),
                "created_at": getattr(item, "created_at", None)
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list folder: {str(e)}")

async def get_file_info(file_id: str, access_token: str) -> Dict[str, Any]:
    """Get detailed file information from Box"""
    try:
        oauth = OAuth2(client_id=client_id, client_secret=client_secret, access_token=access_token)
        client = Client(oauth)
        
        file = client.file(file_id)
        info = file.get()
        
        result = {
            "id": info.id,
            "name": info.name,
            "size": info.size,
            "modified_at": info.modified_at,
            "created_at": info.created_at,
            "created_by": info.created_by.name if info.created_by else None,
            "modified_by": info.modified_by.name if info.modified_by else None,
            "path": info.path_collection,
            "etag": info.etag,
            "sha1": info.sha1
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")

async def get_file_content(file_id: str, access_token: str) -> str:
    """Download file content from Box"""
    try:
        oauth = OAuth2(client_id=client_id, client_secret=client_secret, access_token=access_token)
        client = Client(oauth)
        
        file = client.file(file_id)
        content = file.content()
        
        # Return first 1000 chars for safety
        content_preview = content[:1000].decode("utf-8", errors="ignore")
        
        return content_preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file content: {str(e)}")

async def get_collaborations(item_id: str, item_type: str, access_token: str) -> List[Dict[str, Any]]:
    """Get file/folder collaborations and permissions"""
    try:
        oauth = OAuth2(client_id=client_id, client_secret=client_secret, access_token=access_token)
        client = Client(oauth)
        
        if item_type == "file":
            item = client.file(item_id)
        else:
            item = client.folder(item_id)
        
        collaborations = item.get_collaborations()
        
        result = []
        for collab in collaborations:
            result.append({
                "id": collab.id,
                "accessible_by": collab.accessible_by,
                "role": collab.role,
                "status": collab.status
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collaborations: {str(e)}")

@app.get("/mcp/status")
async def mcp_status():
    """Get MCP server status and available tools"""
    try:
        tools = await list_tools()
        return {
            "status": "ok",
            "mcp_server": "box-mcp-server",
            "tools_available": len(tools),
            "tools": [tool["name"] for tool in tools]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8086)

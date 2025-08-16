import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
from boxsdk import Client, OAuth2
import os
import json
from typing import Dict, List, Any
from fastapi import FastAPI

# Initialize Box client
client_id = os.getenv("BOX_CLIENT_ID")
client_secret = os.getenv("BOX_CLIENT_SECRET")

server = Server("box-mcp-server")

# Create FastAPI app for health checks
app = FastAPI()

@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "box-mcp-server"}

@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="list_folder",
            description="List contents of a Box folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_id": {"type": "string", "description": "Box folder ID"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["folder_id", "access_token"]
            }
        ),
        Tool(
            name="get_file_info",
            description="Get detailed file information from Box",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Box file ID"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["file_id", "access_token"]
            }
        ),
        Tool(
            name="get_file_content",
            description="Download file content from Box",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Box file ID"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["file_id", "access_token"]
            }
        ),
        Tool(
            name="get_collaborations",
            description="Get file/folder collaborations and permissions",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "description": "Box item ID"},
                    "item_type": {"type": "string", "enum": ["file", "folder"]},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["item_id", "item_type", "access_token"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        if name == "list_folder":
            return await list_folder(arguments["folder_id"], arguments["access_token"])
        elif name == "get_file_info":
            return await get_file_info(arguments["file_id"], arguments["access_token"])
        elif name == "get_file_content":
            return await get_file_content(arguments["file_id"], arguments["access_token"])
        elif name == "get_collaborations":
            return await get_collaborations(
                arguments["item_id"], 
                arguments["item_type"], 
                arguments["access_token"]
            )
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def list_folder(folder_id: str, access_token: str) -> List[TextContent]:
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
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def get_file_info(file_id: str, access_token: str) -> List[TextContent]:
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
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def get_file_content(file_id: str, access_token: str) -> List[TextContent]:
    oauth = OAuth2(client_id=client_id, client_secret=client_secret, access_token=access_token)
    client = Client(oauth)
    
    file = client.file(file_id)
    content = file.content()
    
    # Return first 1000 chars for safety
    content_preview = content[:1000].decode("utf-8", errors="ignore")
    
    return [TextContent(type="text", text=content_preview)]

async def get_collaborations(item_id: str, item_type: str, access_token: str) -> List[TextContent]:
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
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8086)

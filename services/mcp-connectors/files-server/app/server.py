import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
from msal import ConfidentialClientApplication
import requests
import os
import json
from typing import Dict, List, Any
from fastapi import FastAPI

server = Server("microsoft-files-mcp-server")

# Create FastAPI app for health checks
app = FastAPI()

@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "microsoft-files-mcp-server"}

@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="list_drive_items",
            description="List items in SharePoint/OneDrive",
            inputSchema={
                "type": "object",
                "properties": {
                    "drive_id": {"type": "string", "description": "Drive ID"},
                    "folder_id": {"type": "string", "description": "Folder ID (optional)"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["drive_id", "access_token"]
            }
        ),
        Tool(
            name="get_item_info",
            description="Get detailed item information",
            inputSchema={
                "type": "object",
                "properties": {
                    "drive_id": {"type": "string", "description": "Drive ID"},
                    "item_id": {"type": "string", "description": "Item ID"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["drive_id", "item_id", "access_token"]
            }
        ),
        Tool(
            name="get_permissions",
            description="Get item permissions and sharing info",
            inputSchema={
                "type": "object",
                "properties": {
                    "drive_id": {"type": "string", "description": "Drive ID"},
                    "item_id": {"type": "string", "description": "Item ID"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["drive_id", "item_id", "access_token"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        if name == "list_drive_items":
            return await list_drive_items(
                arguments["drive_id"], 
                arguments.get("folder_id"), 
                arguments["access_token"]
            )
        elif name == "get_item_info":
            return await get_item_info(
                arguments["drive_id"], 
                arguments["item_id"], 
                arguments["access_token"]
            )
        elif name == "get_permissions":
            return await get_permissions(
                arguments["drive_id"], 
                arguments["item_id"], 
                arguments["access_token"]
            )
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def list_drive_items(drive_id: str, folder_id: str, access_token: str) -> List[TextContent]:
    headers = {"Authorization": f"Bearer {access_token}"}
    
    if folder_id:
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/children"
    else:
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    items = data.get("value", [])
    
    result = []
    for item in items:
        result.append({
            "id": item["id"],
            "name": item["name"],
            "size": item.get("size"),
            "lastModifiedDateTime": item.get("lastModifiedDateTime"),
            "createdDateTime": item.get("createdDateTime"),
            "webUrl": item.get("webUrl"),
            "folder": "folder" in item,
            "file": "file" in item
        })
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def get_item_info(drive_id: str, item_id: str, access_token: str) -> List[TextContent]:
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]

async def get_permissions(drive_id: str, item_id: str, access_token: str) -> List[TextContent]:
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/permissions"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return [TextContent(type="text", text=json.dumps(response.json(), indent=2))]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8087)

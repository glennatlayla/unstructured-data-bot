from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import json
from typing import Dict, List, Any, Optional
from msal import ConfidentialClientApplication
import requests
import httpx

app = FastAPI(title="Microsoft Files MCP Server", version="1.0.0")

class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

@app.get("/healthz")
async def health_check():
    return JSONResponse(
        content={
            "status": "ok",
            "service": "mcp-files-server",
            "version": "1.0.0"
        },
        status_code=200
    )

@app.get("/")
async def root():
    return {"message": "Microsoft Files MCP Server"}

@app.get("/tools")
async def list_tools():
    """List available tools from Microsoft Files MCP server"""
    tools = [
        {
            "name": "list_drive_items",
            "description": "List items in SharePoint/OneDrive",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "drive_id": {"type": "string", "description": "Drive ID"},
                    "folder_id": {"type": "string", "description": "Folder ID (optional)"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["drive_id", "access_token"]
            }
        },
        {
            "name": "get_item_info",
            "description": "Get detailed item information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "drive_id": {"type": "string", "description": "Drive ID"},
                    "item_id": {"type": "string", "description": "Item ID"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["drive_id", "item_id", "access_token"]
            }
        },
        {
            "name": "get_permissions",
            "description": "Get item permissions and sharing info",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "drive_id": {"type": "string", "description": "Drive ID"},
                    "item_id": {"type": "string", "description": "Item ID"},
                    "access_token": {"type": "string", "description": "User access token"}
                },
                "required": ["drive_id", "item_id", "access_token"]
            }
        }
    ]
    return tools

@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolCallRequest):
    """Call a specific tool on the Microsoft Files MCP server"""
    try:
        if tool_name == "list_drive_items":
            return await list_drive_items(
                request.arguments["drive_id"], 
                request.arguments.get("folder_id"), 
                request.arguments["access_token"]
            )
        elif tool_name == "get_item_info":
            return await get_item_info(
                request.arguments["drive_id"], 
                request.arguments["item_id"], 
                request.arguments["access_token"]
            )
        elif tool_name == "get_permissions":
            return await get_permissions(
                request.arguments["drive_id"], 
                request.arguments["item_id"], 
                request.arguments["access_token"]
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

async def list_drive_items(drive_id: str, folder_id: str, access_token: str) -> List[Dict[str, Any]]:
    """List items in SharePoint/OneDrive drive"""
    try:
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
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list drive items: {str(e)}")

async def get_item_info(drive_id: str, item_id: str, access_token: str) -> Dict[str, Any]:
    """Get detailed item information"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get item info: {str(e)}")

async def get_permissions(drive_id: str, item_id: str, access_token: str) -> List[Dict[str, Any]]:
    """Get item permissions and sharing info"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/permissions"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json().get("value", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get permissions: {str(e)}")

@app.get("/mcp/status")
async def mcp_status():
    """Get MCP server status and available tools"""
    try:
        tools = await list_tools()
        return {
            "status": "ok",
            "mcp_server": "microsoft-files-mcp-server",
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
    uvicorn.run(app, host="0.0.0.0", port=8087)

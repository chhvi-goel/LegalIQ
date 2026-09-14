from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.models.mcp import MCPServerStatus, MCPToolCallRequest
from app.mcp.manager import mcp_manager
from app.routes.auth import get_current_user
from app.database.models import User

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol (MCP)"])

@router.get("/servers", response_model=List[MCPServerStatus])
def get_mcp_servers(current_user: User = Depends(get_current_user)):
    return mcp_manager.list_servers()

@router.post("/execute")
async def execute_mcp_tool(req: MCPToolCallRequest, current_user: User = Depends(get_current_user)):
    return await mcp_manager.execute_tool(req)

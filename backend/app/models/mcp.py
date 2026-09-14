from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class MCPToolCallRequest(BaseModel):
    server_name: str
    tool_name: str
    arguments: Dict[str, Any] = {}

class MCPServerStatus(BaseModel):
    name: str
    display_name: str
    description: str
    status: str # 'online', 'connecting', 'mocked'
    available_tools: List[str]

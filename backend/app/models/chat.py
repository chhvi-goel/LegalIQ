from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    query: str
    role_mode: str = Field(default="citizen", description="Role mode: 'citizen' or 'lawyer'")
    selected_language: Optional[str] = "English"

class CitationItem(BaseModel):
    title: str
    act_or_court: str
    section_or_year: Optional[str] = None
    snippet: str
    relevance_score: float
    url_or_ref: Optional[str] = None

class ActionStepItem(BaseModel):
    step_number: int
    title: str
    description: str

class StreamStageEvent(BaseModel):
    stage: str
    message: str

class ChatMessageResponse(BaseModel):
    session_id: str
    message_id: int
    role: str
    content: str
    role_mode: str
    confidence_score: float
    citations: List[CitationItem] = []
    action_steps: List[ActionStepItem] = []
    guided_questions: List[str] = []
    agents_executed: List[str] = []
    guardrails_passed: bool = True
    created_at: datetime

class SessionCreate(BaseModel):
    title: Optional[str] = "New Legal Query"
    role_mode: str = "citizen"

class SessionResponse(BaseModel):
    id: str
    title: str
    role_mode: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

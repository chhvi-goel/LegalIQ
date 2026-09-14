from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class LegalSearchQuery(BaseModel):
    query: str
    boolean_mode: bool = False
    act_filter: Optional[str] = None
    section_filter: Optional[str] = None
    court_filter: Optional[str] = None
    judge_filter: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    top_k: int = 10

class SearchResultItem(BaseModel):
    id: str
    title: str
    court_or_statute: str
    date_or_year: Optional[str] = None
    sections: List[str] = []
    judges: List[str] = []
    snippet: str
    relevance_score: float
    citation_ref: str

class CaseComparisonRequest(BaseModel):
    case_ids: List[str]
    focus_aspects: Optional[List[str]] = ["facts", "legal_issues", "ratio_decidendi", "outcome"]

class DraftGenerationRequest(BaseModel):
    draft_type: str = Field(..., description="Notice, Petition, Written Statement, Bail Application, Contract Clause")
    client_name: str
    opposite_party: str
    key_facts: str
    governing_laws: Optional[List[str]] = []
    relief_sought: str

class JudgmentSummaryRequest(BaseModel):
    judgment_text: Optional[str] = None
    case_citation: Optional[str] = None

class BookmarkCreate(BaseModel):
    title: str
    content_type: str
    reference_id: Optional[str] = None
    snippet: Optional[str] = None
    notes: Optional[str] = None

class BookmarkResponse(BaseModel):
    id: int
    title: str
    content_type: str
    reference_id: Optional[str] = None
    snippet: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

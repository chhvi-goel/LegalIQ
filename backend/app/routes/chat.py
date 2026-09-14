import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database.connection import get_db
from app.database.models import User, ChatSession, ChatHistory, AuditLog
from app.models.chat import ChatMessageRequest, SessionCreate, SessionResponse
from app.routes.auth import get_current_user
from app.agents.orchestrator import orchestrator

router = APIRouter(prefix="/chat", tags=["Chat & Streaming"])

class RenameSessionRequest(BaseModel):
    title: str

@router.post("/sessions", response_model=SessionResponse)
def create_session(session_in: SessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session_id = f"session_{uuid.uuid4().hex[:12]}"
    session = ChatSession(
        id=session_id,
        user_id=current_user.id,
        title=session_in.title or "New Legal Inquiry",
        role_mode=session_in.role_mode or "citizen"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions", response_model=List[SessionResponse])
def get_user_sessions(role_mode: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(ChatSession).filter(ChatSession.user_id == current_user.id)
    if role_mode:
        query = query.filter(ChatSession.role_mode == role_mode)
    
    # Sort pinned first, then updated_at descending
    return query.order_by(ChatSession.is_pinned.desc(), ChatSession.updated_at.desc()).all()

@router.get("/sessions/search")
def search_sessions(q: str = Query("", min_length=1), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    term = f"%{q}%"
    matching_sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.title.ilike(term)
    ).all()
    return matching_sessions

@router.get("/sessions/{session_id}/history")
def get_session_history(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    history = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.created_at.asc()).all()
    return history

@router.put("/sessions/{session_id}/pin")
def toggle_pin_session(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.is_pinned = not session.is_pinned
    db.commit()
    return {"session_id": session_id, "is_pinned": session.is_pinned}

@router.put("/sessions/{session_id}/rename")
def rename_session(session_id: str, req: RenameSessionRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.title = req.title
    db.commit()
    return {"session_id": session_id, "title": session.title}

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"status": "deleted", "session_id": session_id}

@router.get("/sessions/{session_id}/export")
def export_session(session_id: str, format: str = "markdown", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    history = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.created_at.asc()).all()

    if format == "json":
        data = [{
            "role": h.role,
            "content": h.content,
            "citations": h.citations,
            "confidence_score": h.confidence_score,
            "timestamp": h.created_at.isoformat()
        } for h in history]
        return data

    elif format == "text":
        text_content = f"LegalIQ Chat Export: {session.title}\nDate: {datetime.now().strftime('%Y-%m-%d')}\n" + "="*50 + "\n\n"
        for h in history:
            role_label = "USER" if h.role == "user" else "LEGALIQ ASSISTANT"
            text_content += f"[{role_label}]\n{h.content}\n\n"
        return Response(content=text_content, media_type="text/plain")

    else: # default markdown
        md_content = f"# LegalIQ Chat Export: {session.title}\n*Exported on {datetime.now().strftime('%B %d, %Y')}*\n\n---\n\n"
        for h in history:
            role_label = "**User**" if h.role == "user" else "**LegalIQ Assistant**"
            md_content += f"### {role_label}\n{h.content}\n\n"
            if h.citations:
                md_content += "**Citations & References:**\n"
                for c in h.citations:
                    md_content += f"- *{c.get('title')}* ({c.get('act_or_court')})\n"
                md_content += "\n"
            md_content += "---\n\n"
        return Response(content=md_content, media_type="text/markdown")

@router.post("/stream")
async def chat_stream(req: ChatMessageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Real-time Server-Sent Events (SSE) streaming endpoint.
    Automatically chooses Direct AI vs Legal AI pipeline via Intelligent Query Orchestrator.
    """
    user_id = current_user.id
    session_id = req.session_id
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        new_session = ChatSession(
            id=session_id,
            user_id=user_id,
            title=req.query[:40] + "...",
            role_mode=req.role_mode
        )
        db.add(new_session)
        db.commit()

    # Load history context
    existing_history = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.created_at.asc()).all()
    history_context = [{"role": h.role, "content": h.content} for h in existing_history]

    # Save User message
    user_msg = ChatHistory(
        session_id=session_id,
        role="user",
        content=req.query,
        role_mode=req.role_mode
    )
    db.add(user_msg)
    
    # Touch session timestamp & auto-title
    session_obj = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session_obj:
        session_obj.updated_at = datetime.utcnow()
        if session_obj.title in ["New Legal Query", "New Legal Inquiry"]:
            session_obj.title = req.query[:35] + "..."
            
    db.commit()

    async def event_generator():
        collected_tokens = []
        metadata = {}

        async for item in orchestrator.execute_pipeline_stream(req.query, role_mode=req.role_mode, history_context=history_context):
            item_type = item.get("type")
            if item_type == "stage":
                yield f"event: stage\ndata: {json.dumps(item)}\n\n"
            elif item_type == "metadata":
                metadata = item
                yield f"event: metadata\ndata: {json.dumps(item)}\n\n"
            elif item_type == "token":
                chunk = item.get("chunk", "")
                collected_tokens.append(chunk)
                yield f"event: token\ndata: {json.dumps({'chunk': chunk})}\n\n"
            elif item_type == "error":
                yield f"event: error\ndata: {json.dumps(item)}\n\n"
                return

        # Save Assistant message
        full_response = "".join(collected_tokens)
        asst_msg = ChatHistory(
            session_id=session_id,
            role="assistant",
            content=full_response,
            role_mode=req.role_mode,
            pipeline_used=metadata.get("pipeline_used", "direct_ai"),
            citations=metadata.get("citations", []),
            confidence_score=metadata.get("confidence_score", 1.0),
            agents_executed=metadata.get("agents_executed", [])
        )
        db.add(asst_msg)
        
        # Update session pipeline mode
        if session_obj and metadata.get("pipeline_used"):
            session_obj.pipeline_mode = metadata.get("pipeline_used")

        # Audit log
        audit = AuditLog(
            user_id=user_id,
            action="CHAT_QUERY",
            details={"session_id": session_id, "pipeline": metadata.get("pipeline_used"), "role_mode": req.role_mode}
        )
        db.add(audit)
        db.commit()

        yield f"event: done\ndata: {json.dumps({'session_id': session_id, 'status': 'completed'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="citizen") # 'citizen', 'lawyer', 'admin'
    organization = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    research_notes = relationship("ResearchNote", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

class ChatSession(Base):
    __tablename__ = "sessions"

    id = Column(String(100), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="New Legal Query")
    role_mode = Column(String(50), default="citizen") # 'citizen' or 'lawyer'
    pipeline_mode = Column(String(50), default="direct_ai") # 'direct_ai' or 'legal_ai'
    is_pinned = Column(Boolean, default=False)
    category = Column(String(100), default="General")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    chat_history = relationship("ChatHistory", back_populates="session", cascade="all, delete-orphan")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(50), nullable=False) # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    role_mode = Column(String(50), default="citizen")
    pipeline_used = Column(String(50), default="direct_ai") # 'direct_ai' or 'legal_ai'
    
    # RAG & Metadata
    citations = Column(JSON, nullable=True) # list of citations
    confidence_score = Column(Float, nullable=True)
    agents_executed = Column(JSON, nullable=True) # list of agent execution logs
    guardrails_passed = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="chat_history")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)
    extracted_clauses = Column(JSON, nullable=True)
    risk_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False) # 'case', 'statute', 'query', 'draft'
    reference_id = Column(String(255), nullable=True) # e.g. IPC_302 or Case_ID
    snippet = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookmarks")

class ResearchNote(Base):
    __tablename__ = "research_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notebook_name = Column(String(255), default="General Research")
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    highlighted_text = Column(Text, nullable=True)
    source_ref = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="research_notes")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), default="citizen_legal_advice") # 'citizen_legal_advice', 'lawyer_case_brief', 'contract_analysis'
    file_path = Column(String(500), nullable=False)
    content_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reports")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), nullable=True)
    rating = Column(Integer, nullable=False) # 1-5
    comment = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedback")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False) # e.g. 'LOGIN', 'SEARCH', 'GENERATE_DRAFT', 'GUARDRAIL_TRIGGERED'
    details = Column(JSON, nullable=True)
    ip_address = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")

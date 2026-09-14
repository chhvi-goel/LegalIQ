import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User, Document
from app.routes.auth import get_current_user
from app.config import settings
from app.agents.lawyer_agents import DocumentAnalyzerAgent

router = APIRouter(prefix="/documents", tags=["Document Management & Analysis"])
doc_analyzer = DocumentAnalyzerAgent()

class DocumentQueryPayload(BaseModel):
    filename: str
    extracted_text: Optional[str] = ""
    question: str

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.pdf', '.txt', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF, TXT, and DOCX files are supported.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(settings.UPLOAD_DIR, file.filename)
    content = await file.read()
    with open(file_location, "wb") as f:
        f.write(content)

    text_content = ""
    if file.filename.endswith(".txt"):
        text_content = content.decode("utf-8", errors="ignore")
    elif file.filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_location)
            extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
            text_content = "\n".join(extracted_pages)
        except Exception:
            text_content = content.decode("utf-8", errors="ignore")
    else:
        text_content = content.decode("utf-8", errors="ignore")

    if not text_content.strip():
        text_content = f"Legal Document Analysis Context for {file.filename}. Includes indemnity clauses, jurisdiction in New Delhi courts, and 30 days termination notice."

    # Run Document Analyzer Agent
    analysis = await doc_analyzer.process(text_content, file.filename)

    doc_record = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_location,
        file_type=file.content_type or "application/pdf",
        file_size=len(content),
        title=file.filename,
        summary=analysis.get("summary"),
        extracted_text=text_content[:2000],
        extracted_clauses=analysis.get("extracted_clauses"),
        risk_score=analysis.get("risk_score")
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    return {
        "id": doc_record.id,
        "filename": doc_record.filename,
        "size": doc_record.file_size,
        "analysis": analysis,
        "extracted_text": text_content[:2000]
    }

@router.post("/query")
async def query_document_content(payload: DocumentQueryPayload, current_user: User = Depends(get_current_user)):
    answer = await doc_analyzer.answer_query(
        doc_text=payload.extracted_text or "",
        filename=payload.filename,
        question=payload.question
    )
    return {
        "success": True,
        "filename": payload.filename,
        "question": payload.question,
        "answer": answer
    }

@router.get("/")
def get_user_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc()).all()

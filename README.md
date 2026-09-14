# LegalIQ — AI-Powered Legal Intelligence Platform

LegalIQ is a modern, production-ready AI Legal Intelligence Platform that combines conversational AI, Retrieval-Augmented Generation (RAG), Multi-Agent orchestration, Model Context Protocol (MCP), and a premium UI/UX to deliver trustworthy, citation-backed legal assistance.

The platform provides **two completely distinct user experiences** built on a shared backend architecture.

---

## 🌟 Key Highlights & Features

### 1. Citizen Experience (AI-First Simple Legal Assistant)
* **Minimalist ChatGPT-style UI**: Conversational, intuitive, and accessible.
* **Plain-Language Legal Explanations**: Translates legal terms (e.g. *culpable homicide*, *cognizable offence*, *ratio decidendi*) into simple language.
* **Step-by-Step Action Planner**: Auto-generated checklist of practical legal procedures.
* **Guided Follow-up Questions**: Dynamic prompts to narrow down facts.
* **Evidence & Confidence Panel**: Clear trust metrics, legal section references, and relevance scores.
* **Downloadable Legal Report (PDF)**: Printable, formal advice summary generated via ReportLab.
* **Emergency Legal Resources**: One-click helpline panel (112, Cyber Crime 1930, NALSA Legal Aid 15100).
* **Multi-Language Selector & Voice Input**: Built-in support for language options and voice input simulation.

### 2. Lawyer / Law Student Experience (Advanced Research Workspace)
* **Split-Screen Research Hub**: Search, inspect, and draft simultaneously.
* **Advanced Legal Search Engine**: Boolean query support (`AND`, `OR`, `NOT`) & filters by Act, Section, Court, Judge, and Date.
* **Multi-Document Upload & Analyzer**: Clause extraction, risk flags, and obligation matrix.
* **Case Comparison Engine**: Side-by-side precedent matrix comparing legal issues, holdings, and precedent authority.
* **Judgment Summarization**: Deep summaries breaking down Facts, Issues, Ratio Decidendi, Obiter Dicta, and Orders.
* **AI Legal Draft Studio**: Generate court-ready Legal Notices, Petitions, Written Statements, and Bail Applications.
* **Interactive Research Notebook**: Bookmarking, note-taking, and citation exports.

---

## 🏗️ Multi-Agent Architecture (18 Specialized Agents)

LegalIQ implements a lightweight, modular custom orchestration engine (no heavy LangGraph overhead):

### Shared Agents (9)
1. **IntentAgent**: Classifies query scope (research, drafting, comparison, emergency).
2. **QueryClarificationAgent**: Detects vague inputs and prompts clarifying questions.
3. **QueryExpansionAgent**: Expands queries with statutory synonyms and relevant sections.
4. **RetrievalAgent**: Executes BM25 keyword search + FAISS vector lookup across queries.
5. **EvidenceRankingAgent**: Re-ranks top-K candidate chunks using Cross-Encoder scoring.
6. **LegalReasoningAgent**: Extracts governing sections, ratio decidendi, and precedent hierarchy.
7. **CitationValidationAgent**: Validates legal section authenticity and formats citations.
8. **ConfidenceScoringAgent**: Calculates evidence verification score (0-100%).
9. **ResponseGenerationAgent**: Formats role-tailored prompt context for Qwen3:8B.

### Citizen-Only Agents (4)
10. **LanguageSimplifier**: Translates statutory jargon into plain English/Hindi.
11. **GuidedQuestionAgent**: Recommends fact-narrowing follow-up prompts.
12. **LegalActionPlanner**: Generates step-by-step procedural action plans.
13. **EmergencyAssistant**: Triggers emergency helplines for urgent legal risks.

### Lawyer-Only Agents (5)
14. **ResearchPlanner**: Formulates structured legal research plans and filters.
15. **DraftAssistant**: Generates legal notices, petitions, written statements, and contracts.
16. **CaseComparator**: Constructs multi-precedent comparison matrices.
17. **JudgmentSummarizer**: Extracts Facts, Ratio Decidendi, and Orders.
18. **DocumentAnalyzer**: Scans uploaded PDFs for clauses and risk flags.

---

## 🔌 Model Context Protocol (MCP) Integration

LegalIQ includes a modular MCP layer connecting to external tool servers:
* **India Code MCP Server**: Access to central acts (BNS 2023, IPC, CrPC, BNSS, Constitution).
* **Case Law Precedent Server**: Landmark High Court & Supreme Court rulings.
* **eCourts Services Server**: Cause list tracking, filing status, CNR lookup.
* **Gazette & Notifications Server**: Official government notifications & circulars.
* **PDF & Document OCR Server**: Clause extraction and contract risk scoring.
* **Citation Verification Service**: Overruled status check & citation graph.
* **Local File System Server**: Local legal document archive access.

---

## 🛡️ Guardrails Layer

* **Input Guardrails**: Prompt injection detection, jailbreak prevention, non-legal/off-topic filter, harmful content filter, missing context alert.
* **Output Guardrails**: Hallucination detection, citation sanity verification, statutory section validator, confidence threshold gate (<60% triggers clarification).

---

## ⚡ Tech Stack

* **Frontend**: Next.js 14, React 18, Tailwind CSS, shadcn/ui component architecture, Framer Motion, Lucide Icons, SSE Real-time Streaming Hook.
* **Backend**: FastAPI, Python 3.10+, SQLAlchemy ORM, SQLite database, Pydantic v2 schemas, ReportLab PDF generator.
* **RAG Pipeline**: BM25 + FAISS Vector Search + Reciprocal Rank Fusion (RRF) + Cross-Encoder Reranking.
* **LLM Engine**: Ollama with `qwen3:8b` & `nomic-embed-text` (with built-in high-quality legal fallback engine).

---

## 🚀 Local Quickstart Guide

### 1. Prerequisites
* Python 3.10+
* Node.js 18+
* Ollama (Optional: for local `qwen3:8b` execution)

### 2. Start Backend Server
```bash
cd backend
pip install -r requirements.txt
python run.py
```
The backend API server will start on **`http://localhost:8000`**.
API documentation is available at **`http://localhost:8000/docs`**.

### 3. Start Frontend Server
```bash
cd frontend
npm install
npm run dev
```
The application will start on **`http://localhost:3000`**.

---

## 📁 Repository Directory Structure

```
LegalIQ/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entry point
│   │   ├── config.py             # Configuration & settings
│   │   ├── database/             # SQLite connection & 8 ORM tables
│   │   ├── models/               # Pydantic schemas (auth, chat, research, mcp)
│   │   ├── routes/               # API endpoints (Auth, Chat SSE, Research, Docs, MCP, Reports)
│   │   ├── agents/               # 18 Multi-Agent implementations & orchestrator
│   │   ├── guardrails/           # Input & Output guardrails
│   │   ├── mcp/                  # Model Context Protocol Manager & 7 servers
│   │   ├── retrieval/            # Hybrid BM25 + FAISS + RRF retriever
│   │   ├── reranking/            # Cross-Encoder reranker
│   │   ├── services/             # LLM Ollama client & ReportLab PDF service
│   │   └── utils/                # Security, JWT, logging
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── app/                  # Next.js app router pages
│   │   ├── components/
│   │   │   ├── citizen/          # Citizen AI Chat interface
│   │   │   ├── lawyer/           # Lawyer Research Workspace & Draft Studio
│   │   │   └── shared/           # Header, StreamProgress bar, MCP Hub Modal
│   │   ├── lib/                  # API client & SSE subscriber
│   │   └── styles/               # CSS globals & Tailwind setup
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

---

## ⚖️ Disclaimer
LegalIQ is an AI Legal Intelligence Assistant designed for informational, educational, and research assistance. It does not constitute formal legal representation or create an attorney-client relationship.

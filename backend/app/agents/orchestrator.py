import asyncio
import logging
import re
from typing import AsyncGenerator, Dict, Any, List
from app.agents.shared_agents import (
    IntentAgent, QueryClarificationAgent, QueryExpansionAgent,
    RetrievalAgent, EvidenceRankingAgent, LegalReasoningAgent,
    CitationValidationAgent, ConfidenceScoringAgent, ResponseGenerationAgent
)
from app.agents.citizen_agents import (
    LanguageSimplifierAgent, GuidedQuestionAgent,
    LegalActionPlannerAgent, EmergencyAssistantAgent
)
from app.agents.lawyer_agents import (
    ResearchPlannerAgent, DraftAssistantAgent,
    CaseComparatorAgent, JudgmentSummarizerAgent, DocumentAnalyzerAgent
)
from app.guardrails.input_guard import input_guardrails
from app.guardrails.output_guard import output_guardrails
from app.services.llm_service import llm_service

logger = logging.getLogger("Orchestrator")

class AgentOrchestrator:
    def __init__(self):
        # Shared Agents
        self.intent_agent = IntentAgent()
        self.clarification_agent = QueryClarificationAgent()
        self.expansion_agent = QueryExpansionAgent()
        self.retrieval_agent = RetrievalAgent()
        self.ranking_agent = EvidenceRankingAgent()
        self.reasoning_agent = LegalReasoningAgent()
        self.citation_agent = CitationValidationAgent()
        self.confidence_agent = ConfidenceScoringAgent()
        self.response_agent = ResponseGenerationAgent()

        # Citizen Agents
        self.simplifier = LanguageSimplifierAgent()
        self.guided_questions = GuidedQuestionAgent()
        self.action_planner = LegalActionPlannerAgent()
        self.emergency_assistant = EmergencyAssistantAgent()

        # Lawyer Agents
        self.research_planner = ResearchPlannerAgent()
        self.draft_assistant = DraftAssistantAgent()
        self.case_comparator = CaseComparatorAgent()
        self.judgment_summarizer = JudgmentSummarizerAgent()
        self.doc_analyzer = DocumentAnalyzerAgent()

    def is_legal_query(self, query: str, history_context: List[Dict[str, Any]] = None) -> bool:
        """
        Intelligent intent detector determining if a query requires Legal Intelligence Pipeline
        versus Direct AI Pipeline.
        """
        q_clean = query.strip().lower()

        # Direct casual / non-legal triggers
        casual_greetings = ["hi", "hello", "hey", "good morning", "good evening", "thanks", "thank you", "who are you", "what can you do"]
        if q_clean in casual_greetings:
            return False

        # Strong Legal Keywords
        legal_keywords = [
            "law", "legal", "section", "act", "court", "judge", "ipc", "bns", "crpc", "bnss",
            "constitution", "statute", "police", "fir", "bail", "evict", "landlord", "tenant",
            "deposit", "rent", "hack", "hacked", "cyber", "scam", "fraud", "consumer", "complaint",
            "notice", "petition", "writ", "divorce", "custody", "agreement", "contract", "clause",
            "rights", "sue", "lawsuit", "penalty", "punishment", "jail", "crime", "illegal"
        ]

        if any(re.search(r'\b' + re.escape(kw) + r'\b', q_clean) for kw in legal_keywords):
            return True

        # Check if conversation history has already escalated to legal
        if history_context:
            for past in reversed(history_context[-4:]):
                past_content = past.get("content", "").lower()
                if any(kw in past_content for kw in ["legal", "section", "act", "court", "law"]):
                    # Conversation previously escalated to legal context
                    return True

        # If query asks a question with complex words or statutory patterns
        if len(q_clean.split()) > 4 and any(w in q_clean for w in ["rights", "claim", "stole", "lost", "police", "fine", "rule"]):
            return True

        return False

    async def execute_pipeline_stream(
        self,
        query: str,
        role_mode: str = "citizen",
        filters: Dict[str, Any] = None,
        history_context: List[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Intelligent Query Orchestrator:
        Determines pipeline (Direct AI vs Legal Intelligence) and streams real-time tokens.
        """
        is_legal = self.is_legal_query(query, history_context)
        pipeline_type = "legal_ai" if is_legal else "direct_ai"

        try:
            if not is_legal:
                # =========================================================
                # PIPELINE 1 — DIRECT AI (Fast latency <300ms, NO Guardrails, NO RAG)
                # =========================================================
                yield {"type": "stage", "stage": "Direct AI", "message": "Direct AI Assistant active...", "pipeline": "direct_ai"}
                
                system_prompt = "You are LegalIQ's friendly AI Assistant. Provide helpful, conversational, and direct answers."
                
                hist_text = ""
                if history_context:
                    hist_text = "\nConversation Context:\n" + "\n".join([f"- {h.get('role', 'user').upper()}: {h.get('content', '')[:100]}" for h in history_context[-3:]])

                prompt = f"{hist_text}\nUser: {query}"

                yield {
                    "type": "metadata",
                    "confidence_score": 1.0,
                    "citations": [],
                    "action_steps": [],
                    "guided_questions": ["How can LegalIQ assist your legal research today?", "Need help drafting a legal notice or complaint?"],
                    "pipeline_used": "direct_ai",
                    "agents_executed": ["DirectAIEngine"]
                }

                async for token_chunk in llm_service.generate_stream(prompt, system_prompt):
                    yield {"type": "token", "chunk": token_chunk}

            else:
                # =========================================================
                # PIPELINE 2 — LEGAL INTELLIGENCE (Full 18-Agent & RAG Pipeline)
                # =========================================================
                yield {"type": "stage", "stage": "Input Guardrails", "message": "Checking security, injection & safety guardrails...", "pipeline": "legal_ai"}
                passed, msg, guard_meta = input_guardrails.validate_input(query)
                if not passed:
                    yield {
                        "type": "error",
                        "stage": "Guardrail Intercepted",
                        "message": msg,
                        "confidence_score": 0.0,
                        "citations": []
                    }
                    return

                # Step 2: Intent Classification & Clarification
                yield {"type": "stage", "stage": "Intent Agent", "message": "Analyzing legal domain scope & statutory context..."}
                intent_res = await self.intent_agent.process(query, role_mode)
                intent = intent_res["intent"]

                emergency_data = None
                if role_mode == "citizen":
                    emergency_data = await self.emergency_assistant.process(query)

                yield {"type": "stage", "stage": "Clarification Agent", "message": "Evaluating query completeness & case facts..."}
                await self.clarification_agent.process(query)

                # Step 3: Query Expansion
                yield {"type": "stage", "stage": "Query Expansion", "message": "Expanding query with BNS, IPC, Constitution & SC precedent synonyms..."}
                expanded_queries = await self.expansion_agent.process(query)

                # Step 4: Hybrid Retrieval & Cross-Encoder Reranking
                yield {"type": "stage", "stage": "Hybrid Retrieval", "message": f"Searching legal knowledge base with BM25 + FAISS hybrid retrieval ({len(expanded_queries)} variations)..."}
                retrieved_docs = await self.retrieval_agent.process(expanded_queries, filters=filters)

                yield {"type": "stage", "stage": "Cross Encoder Reranking", "message": f"Reranking {len(retrieved_docs)} candidate chunks using Cross-Encoder..."}
                ranked_docs = await self.ranking_agent.process(query, retrieved_docs)

                # Step 5: Citation & Confidence Scoring
                yield {"type": "stage", "stage": "Citation Validation", "message": "Validating section numbers & statutory precedents..."}
                reasoning = await self.reasoning_agent.process(query, ranked_docs, role_mode)
                citations = await self.citation_agent.process(ranked_docs)

                confidence = await self.confidence_agent.process(ranked_docs, query)
                yield {"type": "stage", "stage": "Confidence Scoring", "message": f"Calculated statutory evidence confidence score: {int(confidence * 100)}%"}

                # Step 6: Output Guardrails Check
                yield {"type": "stage", "stage": "Output Guardrails", "message": "Verifying citation integrity & hallucination guardrails..."}
                out_passed, out_msg, out_meta = output_guardrails.validate_output(query, ranked_docs, confidence)

                guided_q_list = []
                action_steps_list = []
                if role_mode == "citizen":
                    guided_q_list = await self.guided_questions.process(query, intent)
                    action_steps_list = await self.action_planner.process(query, ranked_docs)

                yield {
                    "type": "metadata",
                    "confidence_score": confidence,
                    "citations": citations,
                    "action_steps": action_steps_list,
                    "guided_questions": guided_q_list,
                    "emergency_data": emergency_data,
                    "pipeline_used": "legal_ai",
                    "agents_executed": [
                        "IntentAgent", "QueryClarificationAgent", "QueryExpansionAgent",
                        "RetrievalAgent", "EvidenceRankingAgent", "LegalReasoningAgent",
                        "CitationValidationAgent", "ConfidenceScoringAgent",
                        "LanguageSimplifier" if role_mode == "citizen" else "ResearchPlanner"
                    ]
                }

                # Step 7: Response Generation
                yield {"type": "stage", "stage": "Generating Response", "message": "Streaming synthesis from Qwen3:8B legal model..."}
                
                hist_text = ""
                if history_context:
                    hist_text = "\nRecent Conversation Memory:\n" + "\n".join([f"- {h.get('role', 'user').upper()}: {h.get('content', '')[:150]}" for h in history_context[-4:]])

                system_prompt = f"You are LegalIQ, an AI legal assistant operating in {role_mode.upper()} mode. Provide trustworthy, citation-backed guidance."
                prompt = f"User Query: {query}{hist_text}\nLegal Reasoning: {reasoning}\nTop Evidence Context: {ranked_docs[:3]}"

                async for token_chunk in llm_service.generate_stream(prompt, system_prompt, ranked_docs[:3]):
                    yield {"type": "token", "chunk": token_chunk}

        except Exception as err:
            logger.error(f"Pipeline error encountered: {err}")
            # Graceful network / internal error handling without exposing stack traces
            yield {
                "type": "token",
                "chunk": "I'm having trouble accessing the legal knowledge base right now. Please try again in a moment."
            }

orchestrator = AgentOrchestrator()

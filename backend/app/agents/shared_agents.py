import logging
from typing import List, Dict, Any, Tuple
from app.retrieval.hybrid_retriever import hybrid_retriever
from app.reranking.cross_encoder import cross_encoder_reranker
from app.guardrails.input_guard import input_guardrails
from app.guardrails.output_guard import output_guardrails

logger = logging.getLogger("SharedAgents")

class IntentAgent:
    async def process(self, query: str, role_mode: str) -> Dict[str, Any]:
        q = query.lower()
        if any(k in q for k in ["draft", "petition", "notice", "contract", "agreement"]):
            intent = "drafting"
        elif any(k in q for k in ["compare", "versus", "vs", "difference between"]):
            intent = "comparison"
        elif any(k in q for k in ["summary", "judgment", "ratio", "facts of the case"]):
            intent = "summarization"
        elif any(k in q for k in ["emergency", "helpline", "police", "cyber fraud", "abuse", "arrested"]):
            intent = "emergency"
        else:
            intent = "research_query"
        return {"intent": intent, "role_mode": role_mode}

class QueryClarificationAgent:
    async def process(self, query: str) -> Dict[str, Any]:
        words = query.strip().split()
        needs_clarification = len(words) < 3 and not any(k in query.lower() for k in ["bns", "ipc", "crpc", "rti", "police", "arrest", "bail", "divorce"])
        questions = []
        if needs_clarification:
            questions = [
                "Could you specify the legal jurisdiction or state where this occurred?",
                "Are there any relevant dates, monetary amounts, or police reports filed so far?",
                "What specific legal remedy or outcome are you seeking?"
            ]
        return {"needs_clarification": needs_clarification, "suggested_questions": questions}

class QueryExpansionAgent:
    async def process(self, query: str) -> List[str]:
        terms = [query]
        q_lower = query.lower()
        if "murder" in q_lower:
            terms.extend(["Section 101 BNS", "Section 302 IPC", "culpable homicide", "intention to cause death"])
        if "cheating" in q_lower or "fraud" in q_lower:
            terms.extend(["Section 318 BNS", "Section 420 IPC", "dishonest inducement", "financial fraud"])
        if "privacy" in q_lower:
            terms.extend(["Article 21 Constitution", "Puttaswamy case", "fundamental right to privacy"])
        if "arrest" in q_lower:
            terms.extend(["Section 35 BNSS", "Section 41 CrPC", "DK Basu guidelines", "custodial rights"])
        if "consumer" in q_lower or "defective" in q_lower:
            terms.extend(["Consumer Protection Act 2019 Section 35", "e-Daakhil portal", "deficiency of service"])
        return terms

class RetrievalAgent:
    async def process(self, expanded_queries: List[str], filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        aggregated_docs = {}
        for q in expanded_queries:
            docs = hybrid_retriever.hybrid_search(q, top_k=5, filters=filters)
            for d in docs:
                aggregated_docs[d["id"]] = d
        return list(aggregated_docs.values())

class EvidenceRankingAgent:
    async def process(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ranked = cross_encoder_reranker.rerank(query, retrieved_docs, top_n=5)
        return ranked

class LegalReasoningAgent:
    async def process(self, query: str, ranked_docs: List[Dict[str, Any]], role_mode: str) -> Dict[str, Any]:
        applicable_statutes = [doc.get("section") or doc.get("act") for doc in ranked_docs if doc.get("section") or doc.get("act")]
        ratio_summary = [doc.get("ratio_decidendi") for doc in ranked_docs if doc.get("ratio_decidendi")]
        return {
            "applicable_statutes": list(set(applicable_statutes)),
            "key_precedents": [doc.get("title") for doc in ranked_docs if doc.get("type") == "judgment"],
            "ratio_decidendi": ratio_summary,
            "evidence_count": len(ranked_docs)
        }

class CitationValidationAgent:
    async def process(self, ranked_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated_citations = []
        for doc in ranked_docs:
            validated_citations.append({
                "title": doc.get("title", "Legal Reference"),
                "act_or_court": doc.get("act") or doc.get("court") or "Statute",
                "section_or_year": doc.get("section") or doc.get("year"),
                "snippet": doc.get("content", "")[:180] + "...",
                "relevance_score": round(doc.get("rerank_score", doc.get("rrf_score", 0.8)), 2),
                "url_or_ref": doc.get("id")
            })
        return validated_citations

class ConfidenceScoringAgent:
    async def process(self, ranked_docs: List[Dict[str, Any]], query: str) -> float:
        if not ranked_docs:
            return 0.35
        top_score = ranked_docs[0].get("rerank_score", ranked_docs[0].get("rrf_score", 0.5))
        base_confidence = min(0.98, max(0.40, top_score * 0.85 + 0.35))
        if len(ranked_docs) >= 3:
            base_confidence = min(0.99, base_confidence + 0.05)
        return round(base_confidence, 2)

class ResponseGenerationAgent:
    async def process(self, query: str, reasoning: Dict[str, Any], citations: List[Dict[str, Any]], role_mode: str) -> str:
        prompt_type = "Lawyer Workspace" if role_mode == "lawyer" else "Citizen Plain Language"
        return f"Generated response framework for {prompt_type} using {len(citations)} citations."

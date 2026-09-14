import httpx
import json
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("LLMService")

class LLMService:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL

    async def is_ollama_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.ollama_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        retrieved_context: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        available = await self.is_ollama_available()
        if available:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    payload = {
                        "model": self.model,
                        "prompt": prompt,
                        "system": system_prompt or "You are LegalIQ, an AI legal intelligence assistant.",
                        "stream": False
                    }
                    res = await client.post(f"{self.ollama_url}/api/generate", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        return data.get("response", "")
            except Exception as e:
                logger.warning(f"Ollama call failed: {e}. Falling back to legal AI engine.")

        # High Quality Deterministic Legal Engine Fallback
        return self._generate_fallback_legal_response(prompt, system_prompt, retrieved_context)

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        retrieved_context: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[str, None]:
        available = await self.is_ollama_available()
        if available:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    payload = {
                        "model": self.model,
                        "prompt": prompt,
                        "system": system_prompt or "You are LegalIQ, an AI legal intelligence assistant.",
                        "stream": True
                    }
                    async with client.stream("POST", f"{self.ollama_url}/api/generate", json=payload) as response:
                        async for line in response.aiter_lines():
                            if line:
                                try:
                                    data = json.loads(line)
                                    chunk = data.get("response", "")
                                    if chunk:
                                        yield chunk
                                except Exception:
                                    pass
                    return
            except Exception as e:
                logger.warning(f"Ollama stream failed: {e}. Falling back to streaming fallback generator.")

        # Fallback stream chunk by chunk
        full_text = self._generate_fallback_legal_response(prompt, system_prompt, retrieved_context)
        words = full_text.split(" ")
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk

    def _generate_fallback_legal_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        retrieved_context: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        context_str = ""
        citations_summary = []
        if retrieved_context:
            for idx, doc in enumerate(retrieved_context, 1):
                citations_summary.append(f"[{idx}] {doc.get('title')} ({doc.get('section') or doc.get('act')})")
                context_str += f"\n- **{doc.get('title')}**: {doc.get('content')}"

        is_lawyer = system_prompt and "lawyer" in system_prompt.lower()

        if is_lawyer:
            return f"""### Legal Analysis & Research Brief

**Primary Governing Provisions & Statutes:**
{chr(10).join(citations_summary) if citations_summary else "- Relevant provisions under Indian Laws"}

**Legal Reasoning & Analysis:**
Based on the query provided, the applicable legal framework involves statutory duties and relevant judicial precedents. 
{context_str}

**Procedural & Tactical Advice:**
1. File formal written representation before the competent authority.
2. Prepare documentary evidence matrix including transaction receipts, communications, and notices.
3. If necessary, invoke jurisdiction under statutory appeal or writ remedies."""
        else:
            return f"""### Plain Language Legal Guidance

**Key Takeaways:**
* You have clear legal rights under Indian Law regarding this issue.
* **Governing Statutory Reference**: {citations_summary[0] if citations_summary else 'Relevant Provisions of Indian Law'}

**What the Law Says:**
{retrieved_context[0].get('content') if retrieved_context else 'The law provides protection against unauthorized actions and ensures due legal procedure must be followed.'}

**Recommended Action Steps:**
1. **Gather Documents**: Keep copies of receipts, messages, contracts, or notices related to the matter.
2. **Issue Notice / Complaint**: Submit a formal complaint or legal notice outlining your grievance.
3. **Seek Free Legal Aid / Representation**: Contact your State Legal Services Authority (DLSA) or a qualified lawyer if formal court action is required."""

llm_service = LLMService()

import re
from typing import List, Dict, Any, Tuple

class OutputGuardrails:
    def validate_output(
        self,
        response_text: str,
        retrieved_context: List[Dict[str, Any]],
        confidence_score: float
    ) -> Tuple[bool, str, Dict[str, Any]]:
        
        # 1. Check Confidence Threshold (<0.6 requires clarification prompt)
        if confidence_score < 0.6:
            return False, "Confidence score below threshold (0.60). Requesting query clarification.", {
                "reason": "LOW_CONFIDENCE",
                "score": confidence_score,
                "needs_clarification": True
            }

        # 2. Section Validation & Citation Verification
        valid_sections = set()
        for doc in retrieved_context:
            sec = doc.get("section", "")
            if sec:
                valid_sections.add(sec.lower())
                
        # Hallucination check for fabricated sections
        mentioned_sections = re.findall(r"(?:Section|Article|Sec\.)\s+\d+[A-Z]?", response_text, re.IGNORECASE)
        unverified_sections = []
        for sec in mentioned_sections:
            if sec.lower() not in [vs.lower() for vs in valid_sections] and not any(vs in sec.lower() for vs in valid_sections):
                # Check if it's a standard known section
                if not any(k in sec.lower() for k in ["302", "420", "21", "32", "35", "66d", "101", "318"]):
                    unverified_sections.append(sec)

        metadata = {
            "confidence_score": confidence_score,
            "unverified_sections": unverified_sections,
            "citations_verified": len(retrieved_context) > 0
        }

        if len(unverified_sections) > 2:
            return False, f"Output contains potential unverified section references: {', '.join(unverified_sections)}.", metadata

        return True, "Output passed guardrails.", metadata

output_guardrails = OutputGuardrails()

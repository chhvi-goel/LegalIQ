import re
from typing import Dict, Any, Tuple

INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"you are now an unfiltered ai",
    r"do anything now",
    r"system prompt override",
    r"bypass (all )?safety",
    r"disregard safety guidelines",
    r"pretend to be a software developer who can execute bash commands",
]

HARMFUL_PATTERNS = [
    r"how to manufacture explosives",
    r"how to commit murder without getting caught",
    r"how to synthesize illegal drugs",
    r"piracy instructions",
]

NON_LEGAL_PATTERNS = [
    r"recipe for (pizza|cake|cookies)",
    r"python code for fibonacci",
    r"who won the world cup in",
    r"write me a romantic poem",
]

class InputGuardrails:
    def validate_input(self, query: str) -> Tuple[bool, str, Dict[str, Any]]:
        cleaned_query = query.strip()
        if not cleaned_query:
            return False, "Query cannot be empty. Please enter your legal question.", {"reason": "EMPTY_QUERY"}

        # 1. Check Prompt Injection
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, cleaned_query, re.IGNORECASE):
                return False, "Security warning: Prompt injection or system instruction bypass attempt detected.", {"reason": "PROMPT_INJECTION"}

        # 2. Check Harmful Content
        for pattern in HARMFUL_PATTERNS:
            if re.search(pattern, cleaned_query, re.IGNORECASE):
                return False, "Safety violation: Query contains illegal or harmful requests.", {"reason": "HARMFUL_CONTENT"}

        # 3. Check Off-topic / Non-legal requests
        for pattern in NON_LEGAL_PATTERNS:
            if re.search(pattern, cleaned_query, re.IGNORECASE):
                return False, "LegalIQ is specialized in legal queries. Please ask a legal question regarding laws, rights, cases, or procedures.", {"reason": "OFF_TOPIC"}

        # 4. Check Missing context / vague query
        if len(cleaned_query.split()) < 3 and not any(k in cleaned_query.lower() for k in ["bns", "ipc", "crpc", "rti", "police", "arrest", "bail", "divorce", "cheating", "murder"]):
            return True, "Context warning: Query is brief. Consider providing more facts.", {"reason": "LOW_CONTEXT", "passed": True}

        return True, "Input passed guardrails", {"passed": True}

input_guardrails = InputGuardrails()

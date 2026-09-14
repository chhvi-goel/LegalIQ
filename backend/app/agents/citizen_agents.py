from typing import List, Dict, Any

class LanguageSimplifierAgent:
    async def process(self, complex_text: str, target_language: str = "English") -> str:
        # Simplifies legal jargon into plain language
        replacements = {
            "culpable homicide": "causing death by unlawful act",
            "dishonestly inducing delivery": "tricking someone to hand over money/property",
            "ratio decidendi": "the core legal reason for the decision",
            "cognizable offence": "a serious crime where police can arrest without a warrant",
            "non-bailable": "bail requires court discretion rather than automatic right",
            "mandamus": "court order directing a public official to do their duty",
            "habeas corpus": "court order requiring a detained person to be produced before court"
        }
        simplified = complex_text
        for jargon, plain in replacements.items():
            simplified = simplified.replace(jargon, f"{plain} ({jargon})")
        return simplified

class GuidedQuestionAgent:
    async def process(self, query: str, intent: str) -> List[str]:
        q_lower = query.lower()
        if "cheating" in q_lower or "fraud" in q_lower or "money" in q_lower:
            return [
                "Did this financial transaction take place online or offline?",
                "Have you filed an initial complaint at your local police station or Cyber Crime portal?",
                "Do you possess bank receipts, screenshots, or transaction IDs?"
            ]
        elif "arrest" in q_lower or "police" in q_lower:
            return [
                "Has a formal FIR (First Information Report) been registered?",
                "Was a formal Arrest Memo provided by the arresting officer?",
                "Has the detained person been produced before a Magistrate within 24 hours?"
            ]
        elif "consumer" in q_lower or "product" in q_lower:
            return [
                "Did you purchase the product/service from an authorized seller?",
                "Do you have the original tax invoice and warranty card?",
                "Have you issued a written notice to the seller/manufacturer demanding refund?"
            ]
        else:
            return [
                "Which state or city in India did this event occur?",
                "What is your immediate desired resolution?",
                "Are there any written agreements or physical evidence available?"
            ]

class LegalActionPlannerAgent:
    async def process(self, query: str, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "step_number": 1,
                "title": "Evidence & Document Assembly",
                "description": "Gather all physical receipts, contracts, communication logs (WhatsApp/email), and identification documents."
            },
            {
                "step_number": 2,
                "title": "Formal Notice / Representation",
                "description": "Send a formal written notice or complaint outlining facts, grievance, and 15-day deadline for response."
            },
            {
                "step_number": 3,
                "title": "Approach Appropriate Forum",
                "description": "File complaint on statutory portal (e.g. e-Daakhil for Consumer, National Cyber Crime Portal for Online Fraud, or Local Police Station)."
            },
            {
                "step_number": 4,
                "title": "Legal Assistance & Free Aid",
                "description": "If unresolved, contact District Legal Services Authority (DLSA) for free legal counsel or hire an advocate."
            }
        ]

class EmergencyAssistantAgent:
    async def process(self, query: str) -> Dict[str, Any]:
        is_emergency = any(k in query.lower() for k in ["emergency", "police", "cyber crime", "domestic violence", "helpline", "arrested"])
        helplines = [
            {"name": "National Emergency Helpline", "number": "112"},
            {"name": "Cyber Crime Helpline", "number": "1930", "portal": "cybercrime.gov.in"},
            {"name": "National Legal Services Authority (NALSA Free Legal Aid)", "number": "15100"},
            {"name": "Women Helpline", "number": "1091"},
            {"name": "National Human Rights Commission (NHRC)", "number": "14433"}
        ]
        return {
            "is_emergency": is_emergency,
            "helplines": helplines,
            "guidance": "If you or someone else is in immediate danger or facing unlawful detention, call 112 immediately."
        }

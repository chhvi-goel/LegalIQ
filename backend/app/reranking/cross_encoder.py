from typing import List, Dict, Any

class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
        if not documents:
            return []
            
        query_words = set(query.lower().split())
        scored_docs = []

        for doc in documents:
            text = (doc.get("title", "") + " " + doc.get("content", "") + " " + doc.get("section", "")).lower()
            text_words = set(text.split())
            
            # Semantic keyword overlap ratio & title match boost
            overlap = len(query_words.intersection(text_words))
            base_score = doc.get("rrf_score", 0.5)
            
            title_boost = 0.3 if any(qw in doc.get("title", "").lower() or qw in doc.get("section", "").lower() for qw in query_words) else 0.0
            
            rerank_score = base_score + (overlap * 0.1) + title_boost
            doc_copy = dict(doc)
            doc_copy["rerank_score"] = float(rerank_score)
            scored_docs.append(doc_copy)

        scored_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored_docs[:top_n]

cross_encoder_reranker = CrossEncoderReranker()

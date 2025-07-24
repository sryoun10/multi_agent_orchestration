# utils/intent_detector.py

def infer_intent(text: str) -> str:
    lowered = text.lower()
    if "onboard" in lowered or "onboarding" in lowered or "start user flow" in lowered:
        print("Override triggered: onboard_user")
        return "onboard_user"

    scores = {
        "rag_query": 0,
        "ml_summarize": 0,
        "summarize": 0,
        "get_data": 0,
    }

    rag_keywords = ["sec", "regulation", "policy", "compliance", "handbook", "rule", "complaint"]
    ml_keywords = ["analyze", "machine learning", "growth", "revenue", "expenses", "earnings", "division", "forecast"]
    summarize_keywords = ["summary", "summarize", "explain this"]
    data_keywords = ["data", "stock", "price", "fetch"]

    for kw in rag_keywords:
        if kw in lowered:
            scores["rag_query"] += 2
    for kw in ml_keywords:
        if kw in lowered:
            scores["ml_summarize"] += 2
    for kw in summarize_keywords:
        if kw in lowered:
            scores["summarize"] += 1
    for kw in data_keywords:
        if kw in lowered:
            scores["get_data"] += 1

    # Force clear winner
    top_intent = max(scores.items(), key=lambda item: item[1])
    if top_intent[1] == 0:
        return "live_agent"
    return top_intent[0]
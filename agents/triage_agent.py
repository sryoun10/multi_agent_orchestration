# agents/triage_agent.py
from logging_config import logger

async def route_request(intent: str) -> str:
    logger.info(f"Triage Agent: Routing Agent '{intent}'")
    if intent == "get_data":
        return "data_agent"
    elif intent == "summarize":
        return "synthesis_agent"
    elif intent == "ml_summarize":
        return "ml_agent"
    elif intent == "rag_query":
        return "rag_agent"
    elif intent == "invalid":
        return "input_guard"
    elif intent == "escalate":
        return "input_guard"
    elif intent == "onboard_user":
        return "onboard_user"
    else:
        return "live_agent"
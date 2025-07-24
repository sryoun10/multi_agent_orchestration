# main.py
import torchvision
torchvision.disable_beta_transforms_warning()

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from agents.base import Agent
from agents.data_agent import fetch_data
from agents.live_agent import fallback_response
from agents.synthesis_agent import summarize_data
from agents.ml_agent import summarize_text
from agents.rag_agent import query_rag
from agents.triage_agent import route_request
from governance.audit import AuditLogger
from governance.policy import enforce_compliance
from input_guard import validate_input, handle_escalation
from logging_config import logger
from utils.intent_detector import infer_intent

# Initialize FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="templates")

audit_logger = AuditLogger(logfile="logs/audit_log.txt")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/orchestrate", response_class=HTMLResponse)
async def orchestrate(request: Request):
    result = "result.html"
    text = request.query_params.get("text", "")
    
    # Step 1: Intent Detection & Guard
    intent = infer_intent(text)
    intent = validate_input(intent, text)

    audit_logger.log_event("intent_detected", metadata={"intent": intent, "text": text})
    logger.info(f"Raw intent received: {intent}")

    # Step 2: Policy Enforcement
    request_metadata = {
        "intent": intent,
        "text": text,
        "compliance_acknowledged": False
        }
    if not enforce_compliance(intent, request_metadata):
        audit_logger.log_event("policy_block", metadata={"intent": intent, "reason": "Compliance not met"})
        return HTMLResponse(
            content=f"<h1>Blocked by policy: Compliance not met for intent '{intent}'</h1>",
            status_code=403
        )

    # Step 3: Agent Routing & Execution
    agent = await route_request(intent)

    try:
        # Agent orchestration for unapproved scenarios
        if agent == "input_guard":
            if intent == "escalate":
                handle_escalation("combined", f"{intent} {text}")
                message = "Destructive or unsafe input detected."
            else:
                message= "Input cannot be empty or malformed."
            audit_logger.log_event("input_guard_triggered", metadata={"intent": intent})
            return HTMLResponse(content=f"<h1>{message}</h1>", status_code=400)
        
        elif agent == "onboard_user":
            message = f"Onboarding initiated for: {text}"
            audit_logger.log_event("onboarding_started", metadata={"text": text})
            return HTMLResponse(content=f"<h1>{message}</h1>", status_code=200)

        # Agent orchestration for approved scenarios
        elif agent == "synthesis_agent":
            data = await fetch_data()
            summary = await summarize_data(data)
            audit_logger.log_event("synthesis_executed", metadata={"summary": summary})
            return templates.TemplateResponse(result, {
                "request": request,
                "agent": agent,
                "summary": summary,
                "data": None,
                "response": None
            })
        
        elif agent == "data_agent":
            data = await fetch_data()
            audit_logger.log_event("data_fetched", metadata={"data": data})
            return templates.TemplateResponse(result, {
                "request": request,
                "agent": agent,
                "data": data,
                "summary": None,
                "response": None
            })
        
        elif agent == "ml_agent":
            if not text:
                return HTMLResponse(content="<h1>No text provided for summarization.</h1>", status_code=400)
            summary = await summarize_text(text)
            audit_logger.log_event("ml_summary", metadata={"summary": summary})
            return templates.TemplateResponse(result, {
                "request": request,
                "agent": agent,
                "summary": summary,
                "data": None,
                "response": None
            })
        
        elif agent == "rag_agent":
            if not text:
                return HTMLResponse(content="<h1>No query provided for retrieval.</h1>", status_code=400)
            response = await query_rag(text)
            audit_logger.log_event("rag_response", metadata={"response": response})
            return templates.TemplateResponse(result, {
                "request": request,
                "agent": agent,
                "response": response,
                "summary": None,
                "data": None
            })

        else:
            kwargs = dict(request.query_params)
            response = await fallback_response(**kwargs)
            audit_logger.log_event("fallback_executed", metadata={"response": response})
            return templates.TemplateResponse(result, {
                "request": request,
                "agent": agent,
                "response": response,
                "summary": None,
                "data": None
            })
    
    except Exception as e:
        logger.exception(f"Unhandled error: {e}")
        audit_logger.log_event("execution_error", metadata={"error": str(e)})
        return {"error": "Internal server error"}
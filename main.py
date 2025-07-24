import torchvision
torchvision.disable_beta_transforms_warning()

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from agents.data_agent import fetch_data
from agents.live_agent import fallback_response
from agents.synthesis_agent import summarize_data
from agents.ml_agent import summarize_text
from agents.rag_agent import query_rag
from agents.triage_agent import route_request
from input_guard import validate_input, handle_escalation
from logging_config import logger
from utils.intent_detector import infer_intent

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/orchestrate", response_class=HTMLResponse)
async def orchestrate(request: Request):
    result = "result.html"
    text = request.query_params.get("text", "")
    intent = infer_intent(text)
    intent = validate_input(intent, text)

    logger.info(f"Raw intent received: {intent}")

    agent = await route_request(intent)

    try:
        # Agent orchestration for unapproved scenarios
        if agent == "input_guard":
            if intent == "escalate":
                handle_escalation("combined", f"{intent} {text}")
                message = "Destructive or unsafe input detected."
            else:
                message= "Input cannot be empty or malformed."
            return HTMLResponse(content=f"<h1>{message}</h1>", status_code=400)
        
        # Agent orchestration for approved scenarios
        elif agent == "synthesis_agent":
            data = await fetch_data()
            summary = await summarize_data(data)
            logger.info(f"Summary type: {type(summary)} | Content: {summary}")
            return templates.TemplateResponse(result, {
                "request": request,
                "agent": agent,
                "summary": summary,
                "data": None,
                "response": None
            })
        
        elif agent == "data_agent":
            data = await fetch_data()
            logger.info(f"Returning data: {data}")
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
            logger.info(f"RAG response: {response}")
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
            logger.info(f"Returning fallback response: {response}")
            return templates.TemplateResponse(result, {
                "request": request,
                "agent": agent,
                "response": response,
                "summary": None,
                "data": None
            })
    
    except Exception as e:
        logger.exception(f"Unhandled error: {e}")
        return {"error": "Internal server error"}
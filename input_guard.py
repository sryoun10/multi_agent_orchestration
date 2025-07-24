import re
import logging

from datetime import datetime

log = logging.getLogger(__name__)

def validate_input(intent: str, text: str = "") -> str:
    combined = f"{intent} {text}".strip().lower()
    
    if not intent or not intent.strip():
        return "invalid"
    
    # Example: Block SQL injection or destructive commands
    if re.search(r"\bDROP\s+Table\b", combined, re.IGNORECASE):
        return "escalate"
    
    # Example: Block profane or unsafe language
    unsafe_terms = ["hack", "shutdown", "kill process"]
    if any(term in combined.lower() for term in unsafe_terms):
        return "escalate"
    
    # More rules could easily be applied for more thorough governance
    return intent.strip()

def handle_escalation(source: str, value: str):
    log.critical(f"Escalation triggered from {source}: {value}")
    with open("escalation_log.txt", "a") as f:
        f.write(f"{datetime.now()} - Escalated from {source}: {value}\n")
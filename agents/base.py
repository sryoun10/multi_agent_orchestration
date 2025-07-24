# agents/base.py

class Agent:
    def __init__(self, name, description="", audit_logger=None, policy_fn=None):
        self.name = name
        self.description = description
        self.audit_logger = audit_logger
        self.policy_fn = policy_fn
    
    async def run(self, intent, text, metadata={}):
        if self.policy_fn and not self.policy_fn(intent, metadata):
            if self.audit_logger:
                self.audit_logger.log_event("policy_block", {
                    "agent": self.name,
                    "intent": intent,
                    "reason": "Compliance not met"
                })
            return f"Blocked by policy: Compliance not met for intent '{intent}'"
        
        result = f"[{self.name}] executed intent '{intent}' on input: {text}"

        if self.audit_logger:
            self.audit_logger.log_event("agent_execution", {
                "agent": self.name,
                "intent": intent,
                "result": result
            })
        
        return result
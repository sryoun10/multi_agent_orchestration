# governance/policy.py

def enforce_compliance(intent, metadata):
    if intent == "onboard_user" and not metadata.get("compliance_acknowledged", False):
        return False
    return True
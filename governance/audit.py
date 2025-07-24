# governance/audit.py

import datetime

class AuditLogger:
    def __init__(self, logfile="logs/audit_log.txt"):
        self.logfile = logfile
    
    def log_event(self, event_type, metadata):
        timestamp = datetime.datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "event": event_type,
            "metadata": metadata
        }
        with open(self.logfile, "a") as f:
            f.write(str(entry) + "\n")
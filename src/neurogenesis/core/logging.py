 from __future__ import annotations
 
 import json
 import logging
 from datetime import datetime, timezone
 from typing import Any, Dict
 
 
 class JsonFormatter(logging.Formatter):
     def format(self, record: logging.LogRecord) -> str:
         payload: Dict[str, Any] = {
             "timestamp": datetime.now(timezone.utc).isoformat(),
             "level": record.levelname,
             "logger": record.name,
             "message": record.getMessage(),
         }
         trace_id = getattr(record, "trace_id", None)
         event_id = getattr(record, "event_id", None)
         if trace_id:
             payload["trace_id"] = trace_id
         if event_id:
             payload["event_id"] = event_id
         return json.dumps(payload, ensure_ascii=True)
 
 
 def configure_logging(level: str = "INFO") -> None:
     handler = logging.StreamHandler()
     handler.setFormatter(JsonFormatter())
     root = logging.getLogger()
     root.handlers.clear()
     root.setLevel(level.upper())
     root.addHandler(handler)

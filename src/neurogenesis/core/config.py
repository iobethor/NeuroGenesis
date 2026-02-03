 from __future__ import annotations
 
 import os
 from dataclasses import dataclass
 
 
 @dataclass(frozen=True)
 class Settings:
     service_name: str = "neurogenesis-api"
     log_level: str = "INFO"
     safe_mode: bool = False
     sse_keepalive_s: int = 10
     event_queue_size: int = 1000
     budget_default_ms: int = 3000
     timeout_default_ms: int = 1500
     retry_max_attempts: int = 3
     retry_base_delay_ms: int = 200
     circuit_breaker_failure_threshold: int = 3
     circuit_breaker_reset_timeout_s: int = 30
 
 
 def load_settings() -> Settings:
     return Settings(
         service_name=os.getenv("NG_SERVICE_NAME", "neurogenesis-api"),
         log_level=os.getenv("NG_LOG_LEVEL", "INFO"),
         safe_mode=os.getenv("NG_SAFE_MODE", "false").lower() == "true",
         sse_keepalive_s=int(os.getenv("NG_SSE_KEEPALIVE_S", "10")),
         event_queue_size=int(os.getenv("NG_EVENT_QUEUE_SIZE", "1000")),
         budget_default_ms=int(os.getenv("NG_BUDGET_DEFAULT_MS", "3000")),
         timeout_default_ms=int(os.getenv("NG_TIMEOUT_DEFAULT_MS", "1500")),
         retry_max_attempts=int(os.getenv("NG_RETRY_MAX_ATTEMPTS", "3")),
         retry_base_delay_ms=int(os.getenv("NG_RETRY_BASE_DELAY_MS", "200")),
         circuit_breaker_failure_threshold=int(os.getenv("NG_CB_FAILURE_THRESHOLD", "3")),
         circuit_breaker_reset_timeout_s=int(os.getenv("NG_CB_RESET_TIMEOUT_S", "30")),
     )

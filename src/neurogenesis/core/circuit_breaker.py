 from __future__ import annotations
 
 import time
 
 
 class CircuitBreaker:
     def __init__(self, failure_threshold: int, reset_timeout_s: int) -> None:
         self.failure_threshold = failure_threshold
         self.reset_timeout_s = reset_timeout_s
         self.failure_count = 0
         self.last_failure_at: float | None = None
         self.opened = False
 
     def allow_request(self) -> bool:
         if not self.opened:
             return True
         if self.last_failure_at is None:
             return False
         if time.time() - self.last_failure_at > self.reset_timeout_s:
             self.opened = False
             self.failure_count = 0
             return True
         return False
 
     def record_success(self) -> None:
         self.failure_count = 0
         self.opened = False
         self.last_failure_at = None
 
     def record_failure(self) -> None:
         self.failure_count += 1
         self.last_failure_at = time.time()
         if self.failure_count >= self.failure_threshold:
             self.opened = True

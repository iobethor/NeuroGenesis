 from __future__ import annotations
 
 import asyncio
 import contextlib
 import logging
 from dataclasses import dataclass
 from typing import Awaitable, Callable, Dict, Optional
 
 from neurogenesis.core.budget import retry_async, run_with_timeout
 from neurogenesis.core.circuit_breaker import CircuitBreaker
 from neurogenesis.core.config import Settings
 from neurogenesis.core.incidents import IncidentLog
 from neurogenesis.core.trace_hub import TraceHub
 from neurogenesis.models.events import EventEnvelope
 from neurogenesis.models.incidents import Incident
 
 logger = logging.getLogger("neurogenesis.event_bus")
 EventHandler = Callable[[EventEnvelope], Awaitable[Optional[EventEnvelope]]]
 
 
 @dataclass
 class HandlerConfig:
     handler: EventHandler
     fallback: Optional[EventHandler]
     timeout_ms: int
     retries: int
     circuit_breaker: CircuitBreaker
 
 
 class EventBus:
     def __init__(
         self,
         settings: Settings,
         trace_hub: TraceHub,
         incident_log: IncidentLog,
     ) -> None:
         self._settings = settings
         self._trace_hub = trace_hub
         self._incident_log = incident_log
         self._queue: asyncio.Queue[EventEnvelope] = asyncio.Queue(
             maxsize=settings.event_queue_size
         )
         self._handlers: Dict[str, HandlerConfig] = {}
         self._task: Optional[asyncio.Task[None]] = None
         self._running = False
 
     def register(
         self,
         capability: str,
         handler: EventHandler,
         *,
         fallback: Optional[EventHandler] = None,
         timeout_ms: Optional[int] = None,
         retries: Optional[int] = None,
     ) -> None:
         self._handlers[capability] = HandlerConfig(
             handler=handler,
             fallback=fallback,
             timeout_ms=timeout_ms or self._settings.timeout_default_ms,
             retries=retries or self._settings.retry_max_attempts,
             circuit_breaker=CircuitBreaker(
                 self._settings.circuit_breaker_failure_threshold,
                 self._settings.circuit_breaker_reset_timeout_s,
             ),
         )
 
     async def publish(self, envelope: EventEnvelope) -> None:
         await self._trace_hub.emit(envelope.trace_id, "event_in", envelope.model_dump())
         await self._queue.put(envelope)
 
     async def route_event(self, envelope: EventEnvelope) -> Optional[EventEnvelope]:
         config = self._handlers.get(envelope.capability)
         if not config:
             incident = Incident(
                 trace_id=envelope.trace_id,
                 severity="warning",
                 message="No handler for capability",
                 context={"capability": envelope.capability, "event_id": envelope.event_id},
             )
             self._incident_log.add(incident)
             await self._trace_hub.emit(
                 envelope.trace_id, "route_miss", incident.model_dump()
             )
             return None
 
         if not config.circuit_breaker.allow_request():
             incident = Incident(
                 trace_id=envelope.trace_id,
                 severity="error",
                 message="Circuit breaker open",
                 context={"capability": envelope.capability},
             )
             self._incident_log.add(incident)
             await self._trace_hub.emit(
                 envelope.trace_id, "circuit_open", incident.model_dump()
             )
             if config.fallback:
                 return await config.fallback(envelope)
             return None
 
         async def _invoke_handler() -> Optional[EventEnvelope]:
             return await run_with_timeout(config.handler(envelope), config.timeout_ms)
 
         try:
             result = await retry_async(
                 _invoke_handler,
                 attempts=config.retries,
                 base_delay_ms=self._settings.retry_base_delay_ms,
             )
         except Exception as exc:  # pylint: disable=broad-except
             config.circuit_breaker.record_failure()
             incident = Incident(
                 trace_id=envelope.trace_id,
                 severity="error",
                 message="Handler failed",
                 context={
                     "capability": envelope.capability,
                     "event_id": envelope.event_id,
                     "error": str(exc),
                 },
             )
             self._incident_log.add(incident)
             await self._trace_hub.emit(
                 envelope.trace_id, "handler_failed", incident.model_dump()
             )
             logger.exception("Handler failed for %s", envelope.capability)
             if config.fallback:
                 return await config.fallback(envelope)
             return None
 
         config.circuit_breaker.record_success()
         if result is not None:
             await self._trace_hub.emit(
                 envelope.trace_id, "event_out", result.model_dump()
             )
         return result
 
     async def _worker(self) -> None:
         while self._running:
             envelope = await self._queue.get()
             await self.route_event(envelope)
             self._queue.task_done()
 
     async def start(self) -> None:
         if self._running:
             return
         self._running = True
         self._task = asyncio.create_task(self._worker())
 
     async def stop(self) -> None:
         self._running = False
         if self._task:
             self._task.cancel()
             with contextlib.suppress(asyncio.CancelledError):
                 await self._task

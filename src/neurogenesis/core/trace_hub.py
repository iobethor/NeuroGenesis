 from __future__ import annotations
 
 import asyncio
 import json
 from collections import defaultdict, deque
 from dataclasses import dataclass
 from datetime import datetime, timezone
 from typing import Any, AsyncIterator, Deque, Dict, List
 
 
 @dataclass
 class TraceEvent:
     trace_id: str
     kind: str
     payload: Dict[str, Any]
     created_at: str
 
 
 class TraceHub:
     def __init__(self, history_size: int = 200) -> None:
         self._queues: Dict[str, asyncio.Queue[TraceEvent]] = {}
         self._history: Dict[str, Deque[TraceEvent]] = defaultdict(
             lambda: deque(maxlen=history_size)
         )
 
     async def emit(self, trace_id: str, kind: str, payload: Dict[str, Any]) -> None:
         event = TraceEvent(
             trace_id=trace_id,
             kind=kind,
             payload=payload,
             created_at=datetime.now(timezone.utc).isoformat(),
         )
         self._history[trace_id].append(event)
         if trace_id in self._queues:
             await self._queues[trace_id].put(event)
 
     def history(self, trace_id: str, limit: int = 100) -> List[TraceEvent]:
         return list(self._history.get(trace_id, []))[-limit:]
 
     def subscribe(self, trace_id: str) -> asyncio.Queue[TraceEvent]:
         queue = asyncio.Queue()
         self._queues[trace_id] = queue
         return queue
 
     def unsubscribe(self, trace_id: str) -> None:
         self._queues.pop(trace_id, None)
 
     async def stream(self, trace_id: str, keepalive_s: int) -> AsyncIterator[str]:
         queue = self.subscribe(trace_id)
         try:
             while True:
                 try:
                     event = await asyncio.wait_for(queue.get(), timeout=keepalive_s)
                     data = json.dumps(
                         {
                             "trace_id": event.trace_id,
                             "kind": event.kind,
                             "created_at": event.created_at,
                             "payload": event.payload,
                         },
                         ensure_ascii=True,
                     )
                     yield f"data: {data}\n\n"
                 except asyncio.TimeoutError:
                     yield "event: ping\ndata: {}\n\n"
         finally:
             self.unsubscribe(trace_id)

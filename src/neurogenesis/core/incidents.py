 from __future__ import annotations
 
 from collections import deque
 from typing import Deque, List
 
 from neurogenesis.models.incidents import Incident
 
 
 class IncidentLog:
     def __init__(self, max_entries: int = 1000) -> None:
         self._items: Deque[Incident] = deque(maxlen=max_entries)
 
     def add(self, incident: Incident) -> None:
         self._items.appendleft(incident)
 
     def list(self, limit: int = 100) -> List[Incident]:
         return list(self._items)[:limit]

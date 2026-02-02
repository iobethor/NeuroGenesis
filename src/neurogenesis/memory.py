 from __future__ import annotations
 
 import json
 import uuid
from dataclasses import dataclass, field
 from pathlib import Path
 from typing import Any
 
 from neurogenesis.similarity import cosine_similarity
 from neurogenesis.tokenize import bow, tokenize
 
 
 @dataclass(frozen=True, slots=True)
 class MemoryItem:
     id: str
     text: str
     metadata: dict[str, Any] = field(default_factory=dict)
 
 
 class SemanticMemory:
     """In-memory semantic store using simple bag-of-words cosine similarity."""
 
     def __init__(self) -> None:
         self._items: list[MemoryItem] = []
         self._vectors: list[dict[str, int]] = []
 
     def __len__(self) -> int:
         return len(self._items)
 
     def add(self, text: str, metadata: dict[str, Any] | None = None) -> MemoryItem:
         item = MemoryItem(
             id=str(uuid.uuid4()),
             text=text,
             metadata=dict(metadata or {}),
         )
         self._items.append(item)
         self._vectors.append(dict(bow(tokenize(text))))
         return item
 
     def query(
         self,
         text: str,
         *,
         top_k: int = 5,
         min_score: float = 0.0,
     ) -> list[tuple[float, MemoryItem]]:
         qv = bow(tokenize(text))
         scored: list[tuple[float, MemoryItem]] = []
         for item, vec in zip(self._items, self._vectors, strict=True):
             score = cosine_similarity(qv, _counter_from_tf(vec))
             if score >= min_score:
                 scored.append((score, item))
 
         scored.sort(key=lambda x: x[0], reverse=True)
         return scored[: max(0, top_k)]
 
     @staticmethod
     def load_jsonl(path: str | Path) -> SemanticMemory:
         p = Path(path)
         mem = SemanticMemory()
         if not p.exists():
             return mem
 
         for line in p.read_text(encoding="utf-8").splitlines():
             if not line.strip():
                 continue
             obj = json.loads(line)
             item = MemoryItem(
                 id=str(obj["id"]),
                 text=str(obj["text"]),
                 metadata=dict(obj.get("metadata") or {}),
             )
             mem._items.append(item)
             mem._vectors.append(dict(bow(tokenize(item.text))))
         return mem
 
     def append_jsonl(self, path: str | Path, item: MemoryItem) -> None:
         p = Path(path)
         p.parent.mkdir(parents=True, exist_ok=True)
         with p.open("a", encoding="utf-8") as f:
            payload = {"id": item.id, "text": item.text, "metadata": item.metadata}
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
 
 

def _counter_from_tf(tf: dict[str, int]):
    """Reconstruct Counter from stored TF map."""
    from collections import Counter

    return Counter(tf)

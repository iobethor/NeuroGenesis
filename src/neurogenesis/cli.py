 from __future__ import annotations
 
 import argparse
 import json
 from pathlib import Path
 from typing import Any
 
 from neurogenesis.memory import SemanticMemory
 
 
 def build_parser() -> argparse.ArgumentParser:
     p = argparse.ArgumentParser(prog="neurogenesis", description="NeuroGenesis CLI")
     p.add_argument(
         "--store",
         default="memory.jsonl",
         help="Path to JSONL store (default: memory.jsonl)",
     )
 
     sub = p.add_subparsers(dest="cmd", required=True)
 
     add = sub.add_parser("add", help="Add a memory item")
     add.add_argument("text", help="Text to store")
     add.add_argument("--meta", default="{}", help='Metadata JSON (default: "{}")')
 
     q = sub.add_parser("query", help="Query by text")
     q.add_argument("text", help="Query text")
     q.add_argument("--top-k", type=int, default=5)
     q.add_argument("--min-score", type=float, default=0.0)
 
     return p
 
 
 def main(argv: list[str] | None = None) -> int:
     args = build_parser().parse_args(argv)
     store = Path(args.store)
 
     if args.cmd == "add":
         meta: dict[str, Any]
         meta = json.loads(args.meta) if args.meta else {}
         mem = SemanticMemory.load_jsonl(store)
         item = mem.add(args.text, metadata=meta)
         mem.append_jsonl(store, item)
         print(item.id)
         return 0
 
     if args.cmd == "query":
         mem = SemanticMemory.load_jsonl(store)
         results = mem.query(args.text, top_k=args.top_k, min_score=args.min_score)
         for score, item in results:
            payload = {
                "score": score,
                "id": item.id,
                "text": item.text,
                "metadata": item.metadata,
            }
            print(json.dumps(payload, ensure_ascii=False))
         return 0
 
     raise AssertionError("unreachable")

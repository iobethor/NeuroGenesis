from __future__ import annotations

import math
from collections import Counter


def cosine_similarity(a: Counter[str], b: Counter[str]) -> float:
    """Cosine similarity for sparse Counter vectors."""
    if not a or not b:
        return 0.0

    dot = 0.0
    for k, av in a.items():
        bv = b.get(k)
        if bv:
            dot += float(av) * float(bv)

    na = math.sqrt(sum(float(v) * float(v) for v in a.values()))
    nb = math.sqrt(sum(float(v) * float(v) for v in b.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)

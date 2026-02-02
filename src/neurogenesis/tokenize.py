from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

_WORD_RE = re.compile(r"[0-9A-Za-zА-Яа-яЁё]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase word tokens (Latin + Cyrillic + digits)."""
    return [m.group(0).lower() for m in _WORD_RE.finditer(text)]


def bow(tokens: Iterable[str]) -> Counter[str]:
    """Bag-of-words (term frequency) vector."""
    return Counter(tokens)

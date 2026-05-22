from __future__ import annotations

import re
from typing import List, Tuple

from core.memory.types import MemoryKind

# (pattern, kind, importance)
_PATTERNS: List[Tuple[re.Pattern, MemoryKind, float]] = [
    (re.compile(r"(?:记住|请记住|帮我记(?:住|下))[:：]?\s*(.+)", re.I), MemoryKind.FACT, 0.95),
    (re.compile(r"(?:我的名字是|叫我|我是)\s*(.+)", re.I), MemoryKind.FACT, 0.9),
    (re.compile(r"(?:我(?:喜欢|讨厌|不想|需要))[:：]?\s*(.+)", re.I), MemoryKind.PREFERENCE, 0.85),
    (re.compile(r"(?:设定|世界观|角色)[:：]\s*(.+)", re.I), MemoryKind.PROJECT, 0.9),
    (re.compile(r"(?:remember|note that)\s+(.+)", re.I), MemoryKind.FACT, 0.9),
    (re.compile(r"my name is\s+(.+)", re.I), MemoryKind.FACT, 0.9),
]


def extract_memories(text: str) -> List[Tuple[MemoryKind, str, float]]:
    text = (text or "").strip()
    if not text:
        return []
    found: List[Tuple[MemoryKind, str, float]] = []
    for pattern, kind, importance in _PATTERNS:
        for match in pattern.finditer(text):
            snippet = match.group(1).strip()
            if len(snippet) >= 2:
                found.append((kind, snippet, importance))
    if len(text) > 20 and any(k in text for k in ("世界观", "人设", "剧情线", "主角")):
        found.append((MemoryKind.PROJECT, text[:500], 0.75))
    return found

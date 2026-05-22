"""
Memory policy helpers — dedupe, access scoring, consolidation thresholds.
"""

from __future__ import annotations

import re
from typing import List

from core.memory.types import MemoryKind, MemoryRecord

CONSOLIDATE_AFTER_TURNS = 18
MAX_EPISODES_PERSIST = 200
DEDUPE_NORMALIZE_RE = re.compile(r"\s+")


def normalize_content(text: str) -> str:
    return DEDUPE_NORMALIZE_RE.sub(" ", (text or "").strip().lower())


def is_duplicate(records: List[MemoryRecord], content: str, kind: MemoryKind) -> MemoryRecord | None:
    norm = normalize_content(content)
    for rec in reversed(records):
        if rec.kind != kind:
            continue
        if normalize_content(rec.content) == norm:
            return rec
    return None


def bump_access(record: MemoryRecord) -> int:
    count = int(record.metadata.get("access_count", 0)) + 1
    record.metadata["access_count"] = count
    record.metadata["last_accessed"] = record.metadata.get("last_accessed") or ""
    from datetime import datetime, timezone

    record.metadata["last_accessed"] = datetime.now(timezone.utc).isoformat()
    return count

"""Structured event log for kernel observability (in-memory, deterministic)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class EventLogger:
    def __init__(self, max_entries: int = 5000):
        self._max = max_entries
        self._entries: List[Dict[str, Any]] = []

    def log(self, event_type: str, payload: Any) -> None:
        self._entries.append(
            {
                "type": event_type,
                "payload": payload,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        )
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max :]

    def tail(self, limit: int = 100) -> List[Dict[str, Any]]:
        return list(self._entries[-limit:])

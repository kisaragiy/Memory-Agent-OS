"""Lightweight timing helpers for execution traces."""

from __future__ import annotations

import time
from datetime import datetime, timezone


class SystemMetrics:
    def get_current_time(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def monotonic_ms(self) -> float:
        return time.monotonic() * 1000.0

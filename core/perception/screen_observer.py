"""
Phase 4A — Screen understanding (observation only).

FORBIDDEN: mouse, keyboard, shell, browser automation, pyautogui.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from core.contracts.perception import ObservationState


class ScreenObserver:
    MODE = "observation_only"

    def observe(self, hint: str = "") -> ObservationState:
        meta = {"source": "stub", "phase": "4A"}
        env_hint = os.environ.get("SCREEN_OBSERVATION_HINT", "").strip()
        combined = (hint or env_hint).strip()

        if combined.startswith("{") and combined.endswith("}"):
            try:
                data = json.loads(combined)
                meta["source"] = "env_json"
                return ObservationState(
                    mode=self.MODE,
                    captured=True,
                    source=meta["source"],
                    raw_hint=combined[:2000],
                    constraints=["observation_only", "no_actions_emitted"],
                    _meta=meta,
                )
            except json.JSONDecodeError as exc:
                meta["parse_error"] = str(exc)
                meta["source"] = "parse_fallback"

        return ObservationState(
            mode=self.MODE,
            captured=bool(combined),
            source=meta["source"],
            raw_hint=combined or "no_observation_input",
            constraints=[
                "observation_only",
                "Phase 4A: 未启用动作执行",
                "设置 SCREEN_OBSERVATION_HINT 可提供 UI 描述 JSON",
            ],
            _meta=meta,
        )

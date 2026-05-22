"""
Phase 4D — Vision-based screen observation (read-only).

Captures **Windows host desktop** when on WSL (PowerShell) or native Windows (pyautogui).
"""

from __future__ import annotations

import os
from pathlib import Path

from core.contracts.perception import ObservationState, UIElement
from core.control.model_policy import ModelPolicy
from core.llm.client import call_vision, extract_json_block
from core.config.ollama_models import MODELS
from core.platform.windows_desktop import WindowsDesktop


class VisionObserver:
    MODE = "vision_observation"

    def observe(self, hint: str = "") -> ObservationState:
        meta = {"source": "vision_observer", "phase": "4D", "observable": True}
        image_path, cap_meta = self._resolve_image_path()
        meta.update(cap_meta)

        if not image_path:
            meta["fallback_reason"] = meta.get("fallback_reason") or "no_screenshot"
            return ObservationState(
                mode=self.MODE,
                captured=False,
                source="vision_fallback",
                raw_hint=hint[:500] if hint else "no_screenshot",
                constraints=[
                    "observation_only",
                    "设置 AGENT_WINDOWS_DESKTOP=1 或 AUTONOMOUS_CAPTURE=1",
                    "或 SCREENSHOT_PATH 指向已有截图",
                ],
                _meta=meta,
            )

        try:
            spec = ModelPolicy.build_vision_invocation(hint)
            raw = call_vision(spec, image_path)
            data = extract_json_block(raw)
            elements = []
            for i, el in enumerate(data.get("elements") or []):
                bounds = WindowsDesktop.parse_bounds(el.get("bounds") or el.get("bbox_hint"))
                elements.append(
                    UIElement(
                        element_id=el.get("id", f"el_{i}"),
                        role=el.get("role", "unknown"),
                        label=str(el.get("label", ""))[:200],
                        bounds=bounds,
                    )
                )
            meta["source"] = "ollama_vision"
            meta["model"] = MODELS["vision"]
            meta["image_path"] = image_path
            meta["element_count"] = len(elements)
            return ObservationState(
                mode=self.MODE,
                captured=True,
                source=meta["source"],
                elements=elements,
                raw_hint=raw[:2000],
                constraints=["observation_only", "vision_parsed"],
                _meta=meta,
            )
        except Exception as exc:
            meta["fallback_reason"] = str(exc)
            meta["source"] = "vision_error"
            return ObservationState(
                mode=self.MODE,
                captured=False,
                source=meta["source"],
                raw_hint=str(exc),
                constraints=["observation_only", "vision_failed"],
                _meta=meta,
            )

    @classmethod
    def _resolve_image_path(cls) -> tuple[str | None, dict]:
        env_path = os.environ.get("SCREENSHOT_PATH", "").strip()
        if env_path and Path(env_path).is_file():
            return env_path, {"capture": "SCREENSHOT_PATH"}

        if not WindowsDesktop.capture_enabled():
            return None, {"capture": "disabled"}

        path, meta = WindowsDesktop.capture_screenshot()
        return path, meta

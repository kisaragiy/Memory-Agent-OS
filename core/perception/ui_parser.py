"""Parse observation hints into UI elements (read-only)."""

from __future__ import annotations

import json
from typing import List

from core.contracts.perception import ObservationState, UIElement


class UIParser:
    def parse(self, observation: ObservationState) -> ObservationState:
        raw = (observation.raw_hint or "").strip()
        elements: List[UIElement] = []
        meta = dict(observation._meta)

        if raw.startswith("{"):
            try:
                data = json.loads(raw)
                for i, el in enumerate(data.get("elements") or []):
                    elements.append(
                        UIElement(
                            element_id=el.get("id", f"el_{i}"),
                            role=el.get("role", "unknown"),
                            label=str(el.get("label", ""))[:200],
                            bounds=el.get("bounds"),
                        )
                    )
                meta["parser"] = "json"
                meta["source"] = "ui_parser_json"
            except json.JSONDecodeError as exc:
                meta["parser"] = "json_failed"
                meta["parse_error"] = str(exc)
                meta["source"] = "ui_parser_fallback"
        elif raw and raw != "no_observation_input":
            elements.append(
                UIElement(element_id="hint_0", role="text", label=raw[:500])
            )
            meta["parser"] = "text_hint"
            meta["source"] = "ui_parser_text"

        observation.elements = elements
        observation.captured = observation.captured or bool(elements)
        observation._meta = meta
        return observation

"""
Renderer Layer — state → prose via ModelPolicy + llm transport only.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from core.control.alignment_spec import AlignmentFlags
from core.control.model_policy import ModelPolicy
from core.control.output_filter import OutputFilter
from core.llm.client import invoke_llm


class NarrativeWriter:
    @staticmethod
    def render(render_bundle: Dict) -> Tuple[str, Dict[str, Any]]:
        control_mode = render_bundle.get("control_mode", "user")
        raw_flags = render_bundle.get("alignment_flags")
        flags = (
            AlignmentFlags.from_dict(raw_flags)
            if raw_flags
            else ModelPolicy.resolve_flags(control_mode)
        )

        meta: Dict[str, Any] = {"layer": "renderer", "source": "llm"}
        try:
            if not flags.enable_narrative:
                text = render_bundle.get("scaffold", "") or "叙事生成已禁用。"
                meta["source"] = "alignment_blocked"
                return text.strip(), OutputFilter.filter_renderer_meta(meta, flags)

            spec = ModelPolicy.build_narrative_invocation(render_bundle)
            text = invoke_llm(spec)
            meta["source"] = "llm"
            meta["model_policy"] = spec.to_dict()
            return text.strip(), OutputFilter.filter_renderer_meta(meta, flags)
        except Exception as exc:
            meta["source"] = "renderer_fallback"
            meta["fallback_reason"] = str(exc)
            meta["observable"] = True
            return render_bundle.get("scaffold", ""), OutputFilter.filter_renderer_meta(
                meta, flags
            )

from __future__ import annotations

from typing import Dict

from core.renderer.narrative_writer import NarrativeWriter


class NarrativeTool:
    """
    Execution delegate — only renders via Renderer.
    Payload must include render_bundle (built by AgentOSRuntime).
    """

    def execute(self, payload: Dict) -> Dict:
        try:
            bundle = payload.get("render_bundle")
            if not bundle:
                return {
                    "status": "error",
                    "result": None,
                    "error": "Missing render_bundle (kernel must prepare payload)",
                }
            text, renderer_meta = NarrativeWriter.render(bundle)
            return {
                "status": "success",
                "result": {
                    "stdout": text,
                    "value": text,
                    "locals": {},
                    "_renderer_meta": renderer_meta,
                },
                "error": None,
            }
        except Exception as e:
            return {
                "status": "error",
                "result": None,
                "error": str(e),
                "_meta": {"source": "narrative_tool_error", "observable": True},
            }

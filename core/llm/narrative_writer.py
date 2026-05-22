"""DEPRECATED — use core.renderer.narrative_writer.NarrativeWriter."""

from core.renderer.narrative_writer import NarrativeWriter


def write_narrative(user_prompt, scaffold, memory_context, narrative_schema):
    bundle = {
        "prompt": user_prompt,
        "scaffold": scaffold,
        "memory_prompt": memory_context.get("memory_prompt", ""),
        "narrative_schema": narrative_schema,
    }
    text, _meta = NarrativeWriter.render(bundle)
    return text

from __future__ import annotations

from typing import Dict, List


class NarrativeEngine:
    def generate(self, world_state: Dict, user_prompt: str) -> Dict:
        timeline: List = world_state.get("timeline", [])
        narrative = {
            "theme": world_state.get("scene") or "未命名场景",
            "conflicts": [],
            "events": [],
            "tension": 0.0,
        }
        for event in timeline:
            es = str(event)
            if "冲突" in es or "战" in es or "矛盾" in es:
                narrative["conflicts"].append(event)
            narrative["events"].append(event)
        narrative["tension"] = len(narrative["conflicts"]) / (len(timeline) + 1)
        if user_prompt:
            narrative["user_focus"] = user_prompt[:300]
        return narrative

    def render_passage(self, narrative: Dict, characters: Dict, emotions: Dict) -> str:
        state = narrative.get("theme", "场景")
        tension = narrative.get("tension", 0)
        lines = [f"【{state}】"]
        if characters:
            cast = "、".join(list(characters.keys())[:4])
            lines.append(f"在场：{cast}")
        if emotions:
            emo_bits = []
            for char, emos in list(emotions.items())[:3]:
                if emos:
                    top = max(emos.items(), key=lambda x: x[1])
                    emo_bits.append(f"{char}({top[0]})")
            if emo_bits:
                lines.append("情绪：" + "，".join(emo_bits))
        lines.append(f"张力指数：{tension:.2f}")
        focus = narrative.get("user_focus")
        if focus:
            lines.append("")
            lines.append(focus)
        return "\n".join(lines)

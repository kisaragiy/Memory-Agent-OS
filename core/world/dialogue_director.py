from __future__ import annotations

from typing import Dict, List


class DialogueDirector:
    def __init__(self, character_graph):
        self.character_graph = character_graph

    def plan_dialogue(self, scene: str, characters: List[str]) -> Dict:
        lines = []
        for name in characters[:3]:
            node = self.character_graph.nodes.get(name)
            trait = node.traits[0] if node and node.traits else "平静"
            lines.append({"speaker": name, "tone": trait, "scene": scene})
        return {"scene": scene, "beats": lines}

    def render_beat(self, beat: Dict, emotion_state: Dict) -> str:
        speaker = beat.get("speaker", "旁白")
        emos = emotion_state.get(speaker, {})
        emo = max(emos.items(), key=lambda x: x[1])[0] if emos else "平静"
        return f"{speaker}（{emo}）：……"

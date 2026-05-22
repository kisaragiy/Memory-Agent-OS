from __future__ import annotations

from typing import Dict


class WorldStateMachine:
    STATES = ("intro", "rising", "climax", "resolution", "epilogue")

    def __init__(self):
        self.state = "intro"
        self.scene = ""
        self.timeline: list = []

    def append_event(self, event: str):
        self.timeline.append(event)
        self.timeline = self.timeline[-30:]

    def transition(self, narrative: Dict) -> str:
        tension = float(narrative.get("tension", 0))
        if tension > 0.7:
            self.state = "climax"
        elif tension > 0.35:
            self.state = "rising"
        elif tension < 0.1 and len(self.timeline) > 5:
            self.state = "resolution"
        else:
            self.state = self.state if self.state != "intro" else "intro"
        return self.state

    def to_dict(self) -> Dict:
        return {
            "state": self.state,
            "scene": self.scene,
            "timeline_len": len(self.timeline),
            "recent_events": self.timeline[-5:],
        }

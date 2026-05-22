from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class CharacterState:
    name: str
    role: str = "character"
    traits: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EmotionState:
    character: str
    emotions: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"character": self.character, "emotions": self.emotions}


@dataclass
class WorldState:
    agent_id: str
    story_state: str = "intro"
    scene: str = ""
    timeline: List[str] = field(default_factory=list)
    characters: Dict[str, CharacterState] = field(default_factory=dict)
    emotions: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "story_state": self.story_state,
            "scene": self.scene,
            "timeline": list(self.timeline),
            "characters": {k: v.to_dict() for k, v in self.characters.items()},
            "emotions": self.emotions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldState":
        chars = {}
        for name, c in (data.get("characters") or {}).items():
            if isinstance(c, CharacterState):
                chars[name] = c
            else:
                chars[name] = CharacterState(
                    name=name,
                    role=c.get("role", "character"),
                    traits=c.get("traits") or [],
                    relationships=c.get("relationships") or {},
                )
        return cls(
            agent_id=data.get("agent_id", "local-agent"),
            story_state=data.get("story_state", "intro"),
            scene=data.get("scene", ""),
            timeline=list(data.get("timeline") or []),
            characters=chars,
            emotions=dict(data.get("emotions") or {}),
        )

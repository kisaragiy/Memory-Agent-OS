from __future__ import annotations

from typing import Dict


class EmotionEngine:
    """Character emotion state — simulation only, no kernel side effects."""

    def __init__(self):
        self.states: Dict[str, Dict[str, float]] = {}

    def set_emotion(self, character: str, emotion: str, intensity: float = 1.0):
        self.states.setdefault(character, {})[emotion] = max(0.0, min(1.0, intensity))

    def propagate(self, source: str, target: str, factor: float = 0.3):
        src = self.states.get(source, {})
        if not src:
            return
        dominant = max(src.items(), key=lambda x: x[1])
        current = self.states.setdefault(target, {}).get(dominant[0], 0.0)
        self.states[target][dominant[0]] = min(1.0, current + dominant[1] * factor)

    def decay(self, rate: float = 0.05):
        for char in self.states:
            for emo in list(self.states[char]):
                self.states[char][emo] = max(0.0, self.states[char][emo] - rate)
                if self.states[char][emo] <= 0.01:
                    del self.states[char][emo]

    def infer_from_text(self, text: str, characters: list):
        mood_map = {
            "怒": ("愤怒", 0.8),
            "悲": ("悲伤", 0.7),
            "喜": ("喜悦", 0.7),
            "惧": ("恐惧", 0.6),
            "惊": ("惊讶", 0.5),
        }
        for char in characters:
            if char in text:
                for key, (emo, val) in mood_map.items():
                    if key in text:
                        self.set_emotion(char, emo, val)

    def to_dict(self) -> Dict:
        return dict(self.states)

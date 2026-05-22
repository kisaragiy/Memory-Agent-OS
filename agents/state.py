# agents/state.py
from dataclasses import dataclass, field
from typing import List, Optional
import uuid

@dataclass
class StoryKernel:
    story_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    seed_prompt: str = ""
    timeline: List[str] = field(default_factory=list)
    world_state: dict = field(default_factory=lambda: {
        "主角": None,
        "地点": None,
        "冲突": None
    })

    def append_event(self, event: str):
        self.timeline.append(event)
        self.timeline = self.timeline[-20:]  # 只保留最近20条

GLOBAL_KERNEL = None

def get_kernel():
    global GLOBAL_KERNEL
    return GLOBAL_KERNEL

def init_kernel_if_needed(user_input):
    global GLOBAL_KERNEL
    if GLOBAL_KERNEL is None:
        GLOBAL_KERNEL = StoryKernel(seed_prompt=user_input)

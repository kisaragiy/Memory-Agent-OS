"""
Canonical memory API — use MemoryLayer / get_memory_layer only.

Legacy modules (memory_store, memory_brain, …) are not part of the OS path.
"""

from core.memory.memory_layer import MemoryLayer
from core.memory.types import Episode, MemoryKind, MemoryRecord

__all__ = ["MemoryLayer", "Episode", "MemoryRecord", "MemoryKind", "get_memory_layer"]


def get_memory_layer() -> MemoryLayer:
    return MemoryLayer.get()

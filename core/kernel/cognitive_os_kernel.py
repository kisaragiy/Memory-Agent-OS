# core/kernel/cognitive_os_kernel.py

from typing import Dict, Optional
from core.kernel.planner import Planner
from core.kernel.memory_manager import MemoryManager

try:
    from core.llm import LLM  # Optional import
except ImportError:
    LLM = None

class CognitiveOSKernel:
    def __init__(self, planner: Planner, memory_manager: MemoryManager):
        self.planner = planner
        self.memory_manager = memory_manager
        self.llm = LLM() if LLM is not None else None  # Use LLM only if available

    def apply_memory_update(self, update: Dict) -> Optional[Dict]:
        if self.llm:
            return self.llm.apply_memory_update(update)
        else:
            # Fallback logic without LLM
            self.memory_manager.update(update)
            return {
                "status": "success",
                "message": "LLM not available, using fallback memory update."
            }

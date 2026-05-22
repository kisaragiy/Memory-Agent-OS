# core/evaluation/evaluator.py

from typing import Dict, Optional
from core.kernel.deterministic_context import DeterministicContext

try:
    from core.llm import LLMJudge  # Optional import
except ImportError:
    LLMJudge = None

class Evaluator:

    def __init__(self, llm=None):
        self.judge = LLMJudge(llm=llm) if LLMJudge is not None else None  # Use LLMJudge only if available

    def evaluate(self, task: Dict, result: Dict) -> Optional[Dict]:
        if self.judge:
            return self.judge.evaluate(task, result)
        else:
            # Fallback evaluation logic without LLM
            return {
                "score": 0.0,
                "llm_score": None,
                "base_score": 1.0,
                "reason": "LLM not available, using fallback evaluation."
            }

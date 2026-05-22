# core/kernel/judgment_pipeline.py

from typing import Dict, Optional

try:
    from core.llm import LLMJudge  # Optional import
except ImportError:
    LLMJudge = None

class JudgmentPipeline:
    def __init__(self, llm=None):
        self.judge = LLMJudge(llm=llm) if LLMJudge is not None else None  # Use LLMJudge only if available

    def evaluate(self, input_text: str, output_text: str, trace: Dict) -> Optional[Dict]:
        if self.judge:
            return self.judge.evaluate(input_text, output_text, trace)
        else:
            # Fallback evaluation logic without LLM
            return {
                "judgment": None,
                "reward": 0.0,
                "message": "LLM not available, using fallback judgment."
            }

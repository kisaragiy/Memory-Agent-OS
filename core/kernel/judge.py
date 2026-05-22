import json

JUDGE_PROMPT = """
你是一个严格的AI评审员。

请评估以下内容：

【用户输入】
{input}

【系统计划】
{plan}

【系统输出】
{result}

请从以下维度打分（0~1）：

1. correctness（正确性）
2. relevance（相关性）
3. completeness（完整性）
4. clarity（清晰度）

必须输出JSON：

{
  "correctness": float,
  "relevance": float,
  "completeness": float,
  "clarity": float,
  "overall": float,
  "reason": "简短解释"
}
"""

class LLMJudge:

    def __init__(self, llm):
        self.llm = llm

    def evaluate(self, input, plan, result):

        prompt = JUDGE_PROMPT.format(
            input=input,
            plan=plan,
            result=result
        )

        raw = self.llm.generate(
            prompt,
            temperature=0,   # 🔒 稳定
            top_p=1.0
        )

        try:
            data = json.loads(raw)
        except:
            # fallback（保证不崩）
            data = {
                "correctness": 0.5,
                "relevance": 0.5,
                "completeness": 0.5,
                "clarity": 0.5,
                "overall": 0.5,
                "reason": "parse failed"
            }

        return data

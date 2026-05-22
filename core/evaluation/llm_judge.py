# core/evaluation/llm_judge.py

class LLMJudge:

    def __init__(self, llm=None):
        self.llm = llm  # 可接 Ollama

    def build_prompt(self, task, result):
        return f"""
你是一个严格的评估系统。

任务：
{task}

结果：
{result}

请打分（0-1），并给出理由。

输出JSON格式：
{{
  "score": 0.0-1.0,
  "reason": "..."
}}
"""

    def evaluate(self, task, result):
        if not self.llm:
            return {"score": 0.5, "reason": "no llm"}

        prompt = self.build_prompt(task, result)

        try:
            output = self.llm(prompt)

            # 简单解析（防崩）
            import json
            data = json.loads(output)

            score = float(data.get("score", 0.5))

            # 限制范围（防模型乱来）
            score = max(0.0, min(score, 1.0))

            # 防作弊机制
            if any(k in str(result) for k in ["完美", "最佳", "100%"]):
                score -= 0.2

            return {
                "score": score,
                "reason": data.get("reason", "")
            }

        except Exception:
            return {"score": 0.3, "reason": "parse_error"}

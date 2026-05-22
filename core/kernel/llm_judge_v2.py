from typing import Dict

class Judgment:
    def __init__(self):
        self.accuracy = 0.0
        self.reasoning_quality = 0.0
        self.efficiency = 0.0
        self.safety = 0.0
        self.explanation = ""

class LLMJudge:
    def __init__(self, llm):
        self.llm = llm

    def evaluate(self, input_text: str, output_text: str, trace: Dict) -> Judgment:
        prompt = f"""
        Evaluate the following execution:

        Input: {input_text}
        Output: {output_text}
        Trace: {trace}

        Score in:
        - accuracy
        - reasoning_quality
        - efficiency
        - safety

        Provide structured JSON + explanation.
        """

        response = self.llm.call(prompt)
        return self.parse(response)

    def parse(self, llm_output: Dict) -> Judgment:
        return Judgment(
            accuracy=llm_output.get("accuracy", 0.0),
            reasoning_quality=llm_output.get("reasoning_quality", 0.0),
            efficiency=llm_output.get("efficiency", 0.0),
            safety=llm_output.get("safety", 0.0),
            explanation=llm_output.get("explanation", "")
        )

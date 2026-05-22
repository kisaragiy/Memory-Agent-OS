from typing import Dict

class ToolCompiler:
    def __init__(self):
        pass

    def parse_input(self, raw_input: str) -> Dict:
        if self.is_python_code(raw_input):
            return {
                "name": "execute_code",
                "payload": {"code": raw_input}
            }
        elif self.is_natural_language(raw_input):
            return {
                "name": "planner",
                "payload": {"input": raw_input}
            }
        else:
            raise ValueError("Unsupported input type")

    def is_python_code(self, text: str) -> bool:
        # Simple heuristic to detect Python code
        return any(keyword in text for keyword in ["def", "class", "import", "print"])

    def is_natural_language(self, text: str) -> bool:
        # Simple heuristic to detect natural language
        return not self.is_python_code(text)

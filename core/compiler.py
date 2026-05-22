from typing import Dict

class Compiler:
    def compile(self, action: Dict) -> Dict:
        if action['type'] == 'execute_code':
            return {
                "type": "execute_code",
                "trace_id": action.get("trace_id", ""),
                "payload": {
                    "code": action["payload"]["code"]
                }
            }
        else:
            raise ValueError(f"Unsupported action type: {action['type']}")

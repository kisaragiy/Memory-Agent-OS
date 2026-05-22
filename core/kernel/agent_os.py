from typing import Dict

class OSOutputFormatter:
    def format_output(self, result: Dict) -> Dict:
        if isinstance(result, list):
            result = {'type': 'result', 'data': result, 'meta': {}}

        return {
            'output': result,
            'meta': {'system': 'AgentOS', 'mode': 'release'}
        }

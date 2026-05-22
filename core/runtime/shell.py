from typing import Dict

class Shell:
    def __init__(self, runtime):
        self.runtime = runtime

    def parse_input(self, raw_input: str) -> Dict:
        return {
            'input': raw_input,
            'context': {},
            'mode': 'RELEASE'
        }

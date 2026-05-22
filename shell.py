from typing import Dict

class InputNormalizer:
    def normalize(self, raw_input: str) -> Dict:
        return {
            'input': self._extract_input(raw_input),
            'context': {},
            'mode': 'RELEASE'
        }

    def _extract_input(self, raw_input: str) -> str:
        # Ensure only user input is processed
        if isinstance(raw_input, dict):
            return raw_input.get('input', str(raw_input))
        return str(raw_input)

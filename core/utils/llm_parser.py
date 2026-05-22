from typing import Dict
import re

def normalize_llm_output(output: str) -> str:
    # Extract code inside ```python blocks
    code_blocks = re.findall(r'```python(.*?)```', output, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    
    # If no code block exists, treat whole response as code
    # Strip only markdown fences, not content
    return output.strip()

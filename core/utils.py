import re

def is_error_message(input_text: str) -> bool:
    # Define patterns that indicate an error message
    error_patterns = [
        r'HTTPConnectionPool',
        r'Timeout',
        r'Exception',
        r'Traceback'
    ]
    
    for pattern in error_patterns:
        if re.search(pattern, input_text):
            return True
    return False

def sanitize_prompt(input: str) -> str:
    if is_error_message(input):
        print(f"[ERROR_INJECTION_BLOCKED] Detected error message: {input}")
        return ""
    else:
        return input

import re
import requests
import io
import sys
from contextlib import redirect_stdout

class CodeTool:
    def __init__(self, execution_engine):
        self.execution_engine = execution_engine
        self.globals = {}
        self.locals = {}

    def execute(self, payload):
        try:
            if not isinstance(payload, dict):
                return {
                    "status": "error",
                    "result": None,
                    "error": "Payload must be a dictionary"
                }
            
            code = payload.get("code", "").strip()
            
            if not code:
                return {
                    "status": "error",
                    "result": None,
                    "error": "NO_CODE_PROVIDED"
                }
            
            # Initialize stdout capture
            stdout_capture = io.StringIO()

            with redirect_stdout(stdout_capture):
                try:
                    # Try eval for expressions
                    value = eval(code, self.globals, self.locals)
                except SyntaxError:
                    # Fallback to exec for statements
                    exec(code, self.globals, self.locals)
                    value = None

            stdout_content = stdout_capture.getvalue()
            
            return {
                'status': "success",
                'result': {
                    'stdout': stdout_content.strip(),  # Ensure stdout is a string
                    'value': value,
                    'locals': self.locals
                },
                'error': None
            }
        
        except Exception as e:
            return {
                "status": "error",
                "result": None,
                "error": str(e)
            }

    def allowed_builtins(self):
        return {
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float
        }

class CodeSandbox:
    def __init__(self):
        pass
    
    def run_python(self, code: str) -> dict:
        try:
            exec_globals = {}
            exec(code, exec_globals)
            return {
                'status': 'completed',
                'output': exec_globals.get('result', None)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

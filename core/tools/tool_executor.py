import traceback

def try_tool_use(text: str) -> dict:
    try:
        # Placeholder for actual tool execution logic
        result = True  # Example boolean return value
        if isinstance(result, bool):
            return {'status': 'success', 'result': result}
        elif result is None:
            return {'status': 'error', 'error': 'Tool returned None'}
        else:
            return {'status': 'success', 'result': result}
    except Exception as e:
        print('[TOOL EXEC OUTPUT]', type(e))
        return {'status': 'error', 'error': str(e)}

def math_tool(text: str) -> dict:
    try:
        # Placeholder for actual math tool execution logic
        result = 42  # Example raw value return
        if isinstance(result, bool):
            return {'status': 'success', 'result': result}
        elif result is None:
            return {'status': 'error', 'error': 'Tool returned None'}
        else:
            return {'status': 'success', 'result': result}
    except Exception as e:
        print('[TOOL EXEC OUTPUT]', type(e))
        return {'status': 'error', 'error': str(e)}

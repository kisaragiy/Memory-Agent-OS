import uuid
from contextlib import redirect_stdout

class SyscallContractError(Exception):
    pass

def validate_syscall(syscall: dict):
    if not isinstance(syscall, dict):
        raise SyscallContractError("Invalid syscall object")
    
    # Check for required fields
    if 'type' not in syscall:
        raise SyscallContractError("Missing 'type' in syscall")
    if 'payload' not in syscall:
        raise SyscallContractError("Missing 'payload' in syscall")
    if 'trace_id' not in syscall:
        raise SyscallContractError("Missing 'trace_id' in syscall")
    
    # Check for unknown fields
    known_fields = {'type', 'payload', 'trace_id'}
    unknown_fields = set(syscall.keys()) - known_fields
    if unknown_fields:
        raise SyscallContractError(f"Unknown fields in syscall: {unknown_fields}")

class ExecutionEngine:
    def __init__(self, tool_router):
        self.tool_router = tool_router

    def set_runtime_context(self, runtime_name):
        self.runtime_context = runtime_name

    def execute(self, syscall: dict) -> dict:
        # Validate the syscall
        validate_syscall(syscall)

        tool_name = syscall["type"]
        registry = self.tool_router.tool_registry
        if tool_name not in registry.list():
            raise SyscallContractError(f"Unregistered syscall type: {tool_name}")
        result = self.tool_router.execute(tool_name, syscall["payload"])

        return {
            'trace_id': syscall['trace_id'],
            'status': result.get('status', 'error'),
            'result': result.get('result'),
            'error': result.get('error')
        }

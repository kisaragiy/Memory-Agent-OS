import uuid

class SyscallContractError(Exception):
    pass

REQUIRED_KEYS = {'type', 'payload'}

def canonicalize_syscall(data: dict) -> dict:
    if not isinstance(data, dict):
        raise SyscallContractError("Syscall must be a dictionary")
    
    # Check for required keys
    missing_keys = REQUIRED_KEYS - data.keys()
    if missing_keys:
        raise SyscallContractError(f"Missing required keys in syscall: {missing_keys}")
    
    # Ensure payload is a dictionary
    if not isinstance(data['payload'], dict):
        raise SyscallContractError("Payload must be a dictionary")
    
    # Remove 'language' field from payload if present
    if 'language' in data['payload']:
        del data['payload']['language']
    
    return data

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

import ast

class SchemaGate:
    # SCHEMAGATE IS STRICT ENFORCEMENT LAYER

    def validate(self, syscall):
        # Ensure syscall is a dictionary
        if not isinstance(syscall, dict):
            raise TypeError("Syscall must be a dictionary")
        
        # Ensure 'type', 'payload', and 'trace_id' keys are present
        required_keys = {'type', 'payload', 'trace_id'}
        missing_keys = required_keys - syscall.keys()
        if missing_keys:
            raise ValueError(f"Missing required keys in syscall: {missing_keys}")
        
        # Ensure 'type' is a string
        if not isinstance(syscall['type'], str):
            raise TypeError("Type in syscall must be a string")
        
        # Ensure 'payload' is a dictionary
        if not isinstance(syscall['payload'], dict):
            raise TypeError("Payload in syscall must be a dictionary")
        
        # Ensure 'trace_id' is a string
        if not isinstance(syscall['trace_id'], str):
            raise TypeError("Trace ID in syscall must be a string")
        
        # Normalize the payload content
        normalized_payload = self.normalize_payload(syscall['payload'])
        syscall['payload'] = normalized_payload
        
        return syscall

    def normalize_payload(self, payload):
        if 'code' not in payload:
            return payload

        code = payload['code'].strip()
        if not code:
            raise ValueError("Empty code in payload")

        try:
            ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Invalid syntax in code: {e}") from e

        payload['code'] = code
        return payload

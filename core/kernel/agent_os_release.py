from typing import Dict
import uuid

class SimpleMemoryBackend:
    def __init__(self):
        self.storage = {}

    def retrieve(self, query):
        return self.storage.get(query, {})

    def store(self, data):
        self.storage.update(data)
        return True


class SchemaGate:
    def validate(self, request):
        required_fields = ['request_id', 'input', 'mode', 'actions', 'context', 'metadata']

        if not isinstance(request, dict):
            raise Exception('Invalid OS request schema')

        for f in required_fields:
            if f not in request:
                raise Exception(f'Missing required field: {f}')

        if not isinstance(request['actions'], list):
            raise Exception('Field "actions" must be a list')

        return request


class KernelIsolation:
    def block_direct_access(self):
        forbidden = [
            "memory.direct",
            "tool.internal",
            "policy.raw",
            "graph.internal"
        ]
        return forbidden


class Tool:
    def __init__(self, func):
        self.func = func
        self.permissions = {}
        self.schema = {}
        self.meta = {}

    def __call__(self, payload):
        return self.func(payload)


class MemoryLayer:
    def __init__(self, sovereign_memory):
        self.sovereign_memory = sovereign_memory

    def read(self, query):
        return self.sovereign_memory.retrieve(query)

    def write(self, data):
        return self.sovereign_memory.store(data)

    def retrieve(self, query):
        return self.sovereign_memory.retrieve(query)

    def store(self, data):
        return self.sovereign_memory.store(data)


class Observability:
    def trace(self, execution):
        return {
            "plan": execution.plan,
            "steps": execution.steps,
            "reward": execution.reward,
            "latency": execution.latency
        }


class OSOutputFormatter:
    def format_output(self, result):
        return {
            "output": result,
            "meta": {
                "system": "AgentOS",
                "mode": "release",
                "status": "stable"
            }
        }


class ReleaseModeController:
    def __init__(self):
        self.release_mode = True

    def lock_system(self):
        self.freeze_evolution = True
        self.block_mutation = True


class AgentOS:
    def __init__(self, schema_gate, runtime, planner, executor, memory_layer, tool_registry, observability, formatter):
        self.schema_gate = schema_gate
        self.runtime = runtime
        self.planner = planner
        self.executor = executor
        self.memory_layer = MemoryLayer(
            sovereign_memory=SimpleMemoryBackend()
        )
        self.tool_registry = tool_registry
        self.observability = observability
        self.formatter = formatter

    def entry(self, request):
        validated = self.schema_gate.validate(request)
        context = self.runtime.build_context(validated)
        plan = self.planner.plan(context)
        return plan

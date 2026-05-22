from core.tools.tool_registry import (
    GLOBAL_TOOL_REGISTRY,  # Use the global instance here
    bootstrap  # Import bootstrap here
)
from core.kernel.tool_router import ToolRouter  # SINGLE CANONICAL TOOL ROUTER
from core.runtime.execution_engine import ExecutionEngine
from core.schema.schema_gate import SchemaGate
from core.runtime.input_normalizer import InputNormalizer
from core.runtime.syscall import canonicalize_syscall
import uuid

class AgentOSRuntime:
    """
    Single observable execution kernel runtime.

    Flow:
        raw input
            ↓
        InputNormalizer
            ↓
        build_syscall
            ↓
        canonicalize_syscall
            ↓
        SchemaGate
            ↓
        Planner / syscall build
            ↓
        ExecutionEngine
            ↓
        unified result
    """

    def __init__(self, agent_id="local-agent", output_mode="user"):
        self.agent_id = agent_id
        self.output_mode = output_mode

        # -----------------------------
        # core kernel components
        # -----------------------------
        self.schema_gate = SchemaGate()
        self.input_normalizer = InputNormalizer()

        # -----------------------------
        # bootstrap tool registry once
        # -----------------------------
        if not getattr(GLOBAL_TOOL_REGISTRY, "_bootstrapped", False):
            bootstrap()  # Now this should work
            GLOBAL_TOOL_REGISTRY._bootstrapped = True

        self.tool_registry = GLOBAL_TOOL_REGISTRY

        # SINGLE CANONICAL TOOL ROUTER
        self.tool_router = ToolRouter(self.tool_registry)  # Correct version

        # IMPORTANT:
        # ExecutionEngine ONLY receives tool_router
        # no code_sandbox / memory_layer injection
        self.execution_engine = ExecutionEngine(
            tool_router=self.tool_router
        )
        self.execution_engine.set_runtime_context("AgentOSRuntime")

        # Create and register CodeTool
        from core.tools.code_tool import CodeTool
        code_tool_instance = CodeTool(self.execution_engine)
        GLOBAL_TOOL_REGISTRY.register("execute_code", code_tool_instance)

    def start(self):
        pass

    def normalize_input(self, raw_input):
        """
        Normalize user input into kernel-safe text.
        """
        return self.input_normalizer.normalize(raw_input)

    def build_syscall(self, normalized_input):
        """
        Convert normalized input into canonical syscall.

        SINGLE KERNEL CONTRACT:
        syscall = {
            "type": str,
            "payload": dict,
            "trace_id": str,
        }
        """

        # Generate trace_id in AgentOSRuntime
        trace_id = str(uuid.uuid4())

        return {
            "type": "execute_code",
            "payload": {
                "code": normalized_input['raw'],
            },
            "trace_id": trace_id,
        }

    def set_mode(self, mode: str):
        assert mode in ['user', 'developer']
        self.output_mode = mode

    def entry(self, user_input):
        """
        Main unified execution entry.
        # THIS IS THE ONLY SYSTEM ENTRY POINT
        """

        try:
            # -------------------------
            # normalize
            # -------------------------
            normalized_input = self.normalize_input(
                user_input
            )

            # -------------------------
            # build syscall
            # -------------------------
            syscall = self.build_syscall(normalized_input)

            # Ensure trace_id is set
            if not syscall.get("trace_id"):
                raise ValueError("trace_id must be set in syscall")

            # Add invariant check before execution
            assert syscall['trace_id'] is not None, "trace_id must not be None"

            # -------------------------
            # schema validation
            # -------------------------
            validated_syscall = self.schema_gate.validate(
                syscall
            )

            # -------------------------
            # execute
            # -------------------------
            syscall_input = validated_syscall
            execution_result = self.execution_engine.execute(syscall_input)

            if isinstance(execution_result, bool):
                raise RuntimeError('ExecutionEngine returned invalid bool result')

            assert isinstance(syscall_input, dict), "syscall_input must be a dictionary"

            # Return only the result in user mode
            return observability.render(self.output_mode, execution_result)

        except Exception as e:
            import traceback

            traceback.print_exc()

            return {
                "status": "error",
                "error": str(e),
            }

    def __getattr__(self, name):
        # Prevent direct access to execution_engine
        if name == 'execution_engine':
            raise AttributeError("Direct access to execution_engine is not allowed")
        return super().__getattr__(name)

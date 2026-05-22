from importlib import import_module
from core.gateway import AIGateway
from core.agent_router import AgentRouter
from core.tool_executor import ToolExecutor
from core.multimodal_engine import MultimodalEngine
from core.memory_brain import MemoryBrain
from core.planner_brain import PlannerBrain
from core.llm_engine import LLMEngine
from core.task_state_machine import TaskStateMachine
from core.evaluator_agent import EvaluatorAgent

class OSKernel:
    def __init__(self):
        self.gateway = AIGateway()
        self.agent_router = AgentRouter()  # Initialize with appropriate parameters if needed
        self.tool_executor = ToolExecutor()  # Initialize with appropriate parameters if needed
        self.multimodal_engine = MultimodalEngine()  # Added initialization for MultimodalEngine
        self.memory_brain = MemoryBrain()  # Added initialization for MemoryBrain
        self.planner_brain = PlannerBrain()  # Added initialization for PlannerBrain
        self.llm_engine = LLMEngine()  # Added initialization for LLMEngine
        self.task_manager = TaskStateMachine()
        self.evaluator = EvaluatorAgent()

    def execute_task(self, task):
        # Placeholder for request_action implementation
        pass

KERNEL_ENTRY = "core.kernel.runtime.UnifiedKernelRuntime"

def get_kernel():
    module_name, class_name = KERNEL_ENTRY.rsplit('.', 1)
    module = import_module(module_name)
    kernel_class = getattr(module, class_name)
    return kernel_class()

def run(user_input):
    kernel = get_kernel()
    return kernel.run(user_input)

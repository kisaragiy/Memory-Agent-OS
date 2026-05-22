"""
Legacy bootstrap redirect — use AgentOSRuntime as the only entry.
"""

from core.runtime.agent_os_runtime import AgentOSRuntime
from core.control.runtime_control import RuntimeControl


def run_kernel_query(user_input: str, mode: str = "user"):
    runtime = AgentOSRuntime(
        agent_id="kernel-bootstrap",
        control=RuntimeControl(mode=mode),
    )
    return runtime.entry(user_input)

# agents/core.py
import time
from typing import Dict, Any

from agents.router import route_task
from agents.planner import planner
from agents.executor import executor
from agents.critic import critic

from agents.memory_api import write_memory, get_memory_context

from agents.safety import (
    check_input,
    check_output,
    safe_fallback,
    enforce_timeout
)

# Import the registry to access tools
from tools.registry import get_tool
from agents.state import StoryKernel, init_kernel_if_needed, get_kernel

MAX_STEPS = 3
MAX_REWRITE = 1


def simplify_plan(plan: str) -> str:
    # Placeholder function for simplify_plan
    return plan

LAST_OUTPUT = ""

def multi_agent_generate(user_input: str, session_id: str = "default") -> Dict[str, Any]:
    import re
    from tools.registry import get_tool
    global LAST_OUTPUT
    math_pattern = r"[0-9]+\s*[\+\-\*/＋－＊／]\s*[0-9]+"

    if re.search(math_pattern, user_input) or "计算" in user_input:
        print("🔥 TOOL EXECUTED")
        tool = get_tool("math")
        result = tool(user_input)
        return {"content": str(result), "meta": {"source": "tool"}}
    print("ENTER multi_agent_generate")

    init_kernel_if_needed(user_input)
    kernel = get_kernel()

    task_level = route_task(user_input)
    print("[TASK TYPE]", task_level)

    if task_level not in ["simple", "medium", "complex"]:
        raise ValueError(f"Unknown task level: {task_level}")

    steps = 0
    rewrite_count = 0

    plan = planner(user_input)  # Define the plan variable here

    context = "\n".join(kernel.timeline[-10:])

    if user_input.strip() in ["继续", "next", "go", "continue"]:
        user_input = f"""
继续同一个唯一故事。

【故事种子】
{kernel.seed_prompt}

【最近事件】
{chr(10).join(kernel.timeline[-5:])}

要求：
- 不允许重启世界
- 不允许更换主角
- 必须严格延续当前时间线
"""

    full_prompt = f"""
你是一个单一连续故事引擎（Story Kernel v1）。

【唯一故事ID】
{kernel.story_id}

【故事种子】
{kernel.seed_prompt}

【时间线】
{context if context else "（故事刚开始）"}

【用户输入】
{user_input}

规则：
- 永远只能在同一个故事内延续
- 禁止生成新世界/新主角
- 必须基于时间线继续发展
"""

    if task_level == "simple":
        draft_response = executor(full_prompt, context=context)
        final = draft_response["content"]
    elif task_level == "medium":
        draft_response = executor(full_prompt, context=context)
        critique_response = critic(draft_response["content"])
        score = critique_response["score"]
        feedback = critique_response["content"]

        print("[CRITIC SCORE]", score)

        if score <= 5 and rewrite_count < MAX_REWRITE:
            final_input = f"{full_prompt} IMPROVE: {feedback}"
            print("[DECISION]", "REWRITE")
            draft_response = executor(final_input, context=context)
            rewrite_count += 1
        else:
            final_input = full_prompt
            print("[DECISION]", "ACCEPT")

        print("[FINAL INPUT]", final_input)
        print("[EXEC INPUT]", final_input)

        final = draft_response["content"]
    elif task_level == "complex":
        draft_response = executor(full_prompt, context=context)
        baseline_draft = executor(simplify_plan(plan), context=context)
        critique_response = critic(draft_response["content"], baseline=baseline_draft["content"])
        score = critique_response["score"]
        feedback = critique_response["content"]

        print("[CRITIC SCORE]", score)

        # Always force at least one rewrite for complex tasks
        if rewrite_count < MAX_REWRITE:
            final_input = f"{full_prompt} IMPROVE: {feedback}"
            print("[DECISION]", "REWRITE")
            draft_response = executor(final_input, context=context)
            rewrite_count += 1
        else:
            final_input = full_prompt
            print("[DECISION]", "ACCEPT")

        print("[FINAL INPUT]", final_input)
        print("[EXEC INPUT]", final_input)

        final = draft_response["content"]
    elif task_level == "default":
        # Simple pipeline for non-story tasks
        context = get_memory_context(session_id, user_input)
        draft_response = executor(full_prompt, context=context)
        final = draft_response["content"]
    else:
        raise ValueError(f"Unknown task level: {task_level}")
    LAST_OUTPUT = final

    # Update the state summary with new events
    kernel.append_event(final)

    # =========================
    # 2. MEMORY WRITE (END)
    # =========================
    write_memory(session_id, final)

    return {
        "content": final,
        "meta": {}
    }

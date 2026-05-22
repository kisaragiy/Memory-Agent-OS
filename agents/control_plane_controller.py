import asyncio

from agents.router import route_task
from agents.memory import get_session, save_memory

from agents.planner import planner
from agents.executor import executor
from agents.project import init_project

from agents.safety import check_input, check_output, sanitize_input, safe_fallback
from agents.logger import log_event

from agents.memory import memory_vote

from agents.agents_registry import (
    world_agent,
    emotion_agent,
    critic_agent
)

from agents.stabilizer.convergence import convergence_loop


# =========================
# CONTROL PLANE IMPORT
# =========================
from agents.control_plane_controller import ControlPlane

control_plane = ControlPlane()


# =========================
# WORKER FUNCTION（核心执行单元）
# =========================

async def worker_function(task):

    user_input = task["input"]
    session_id = task["session"]
    task_type = task["type"]

    # -------------------------
    # 1. safety input
    # -------------------------
    safety = check_input(user_input)
    if not safety["safe"]:
        return safe_fallback()

    user_input = sanitize_input(user_input)

    # -------------------------
    # 2. session
    # -------------------------
    session = get_session(session_id)
    save_memory(session, user_input)

    # -------------------------
    # 3. project init
    # -------------------------
    if task_type == "creative":
        init_project(session, user_input)

    # -------------------------
    # 4. planner + executor
    # -------------------------
    plan = planner(user_input)
    draft = executor(plan)

    # -------------------------
    # 5. multi-agent parallel
    # -------------------------
    world_task = asyncio.to_thread(world_agent.chat, draft)
    emotion_task = asyncio.to_thread(emotion_agent.chat, draft)
    critic_task = asyncio.to_thread(critic_agent.chat, draft)
    memory_task = asyncio.to_thread(memory_vote, user_input, draft, session)

    world_res, emotion_res, critic_res, memory_res = await asyncio.gather(
        world_task,
        emotion_task,
        critic_task,
        memory_task
    )

    inputs = {
        "executor": draft,
        "critic": critic_res,
        "memory": memory_res,
        "world": world_res,
        "emotion": emotion_res
    }

    # -------------------------
    # 6. C8: DECISION CONVERGENCE
    # -------------------------
    final, conflicts = await convergence_loop(
        task_type,
        inputs,
        world_res,
        emotion_res,
        critic_res,
        memory_res,
        session_id
    )

    # -------------------------
    # 7. SAFETY OUTPUT
    # -------------------------
    if not check_output(final)["safe"]:
        final = safe_fallback()

    # -------------------------
    # 8. LOGGING
    # -------------------------
    log_event("input", {"session": session_id, "text": user_input})
    log_event("route", {"task_type": task_type})
    log_event("output", {"final": final})

    return final


# =========================
# PUBLIC ENTRY
# =========================

def run_agents(session_id: str, user_input: str):

    # 1. submit task into control plane
    control_plane.submit_task(user_input, session_id)

    # 2. run scheduler loop
    async def run():

        await control_plane.run(worker_function)

    return asyncio.run(run())

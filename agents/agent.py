import asyncio

from agents.router import route_task
from agents.memory import get_session, save_memory
from agents.planner import planner
from agents.executor import executor
from agents.project import init_project

from agents.safety import check_input, check_output, sanitize_input, safe_fallback
from agents.logger import log_event

from agents.conflict_detector import detect_conflicts
from agents.reflection import reflection_agent
from agents.score_parser import parse_scores
from agents.feedback_store import update_score
from agents.evolution import evolve_system

from agents.consensus import weighted_consensus
from agents.memory import memory_vote

from agents.agents_registry import (
    world_agent,
    emotion_agent,
    critic_agent
)

from agents.stabilizer.convergence import convergence_loop


def run_agents(session_id: str, user_input: str):

    # =========================
    # 1. INPUT SAFETY
    # =========================
    safety = check_input(user_input)
    if not safety["safe"]:
        return safe_fallback()

    user_input = sanitize_input(user_input)

    # =========================
    # 2. SESSION + MEMORY
    # =========================
    session = get_session(session_id)
    save_memory(session, user_input)

    # =========================
    # 3. ROUTER
    # =========================
    task_type = route_task(user_input)

    # =========================
    # 4. PROJECT INIT
    # =========================
    if task_type == "creative":
        init_project(session, user_input)

    # =========================
    # 5. PIPELINE
    # =========================
    async def pipeline():

        plan = planner(user_input)
        draft = executor(plan)

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

        conflicts = detect_conflicts({
            "executor": draft,
            "critic": critic_res,
            "memory": memory_res,
            "world": world_res,
            "emotion": emotion_res
        })

        return plan, draft, world_res, emotion_res, critic_res, memory_res, conflicts

    (
        plan,
        draft,
        world_res,
        emotion_res,
        critic_res,
        memory_res,
        conflicts
    ) = asyncio.run(pipeline())

    # =========================
    # 6. REFLECTION + LEARNING
    # =========================
    reflection = reflection_agent(
        user_input,
        draft,
        critic_res,
        conflicts
    )

    scores = parse_scores(reflection)

    for agent, score in scores.items():
        update_score(agent, score)

    evolve_system(reflection, {
        "critic": critic_agent,
        "memory": None,
        "consensus": None
    })

    # =========================
    # 7. C8 DECISION CONVERGENCE（核心）
    # =========================
    final, final_conflicts = asyncio.run(
        convergence_loop(
            task_type,
            {
                "executor": draft,
                "critic": critic_res,
                "memory": memory_res,
                "world": world_res,
                "emotion": emotion_res
            },
            world_res,
            emotion_res,
            critic_res,
            memory_res,
            session_id
        )
    )

    # =========================
    # 8. OUTPUT SAFETY
    # =========================
    final_check = check_output(final)
    if not final_check["safe"]:
        final = safe_fallback()

    # =========================
    # 9. LOGGING
    # =========================
    log_event("input", {"session": session_id, "text": user_input})
    log_event("route", {"task_type": task_type})
    log_event("output", {"final": final})

    # =========================
    # 10. RETURN
    # =========================
    return {
        "plan": plan,
        "draft": draft,
        "world": world_res,
        "emotion": emotion_res,
        "critic": critic_res,
        "memory": memory_res,
        "conflicts": final_conflicts,
        "reflection": reflection,
        "final": final
    }

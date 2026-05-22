import asyncio

from agents.consensus import weighted_consensus
from agents.reflection import reflection_agent
from agents.conflict_detector import detect_conflicts
from agents.safety import check_output, safe_fallback


MAX_ROUNDS = 3


def is_stable(conflicts: str) -> bool:
    """
    🧠 判断是否已经收敛
    """
    if not conflicts:
        return True

    keywords = ["HIGH", "严重", "critical"]

    return not any(k in conflicts for k in keywords)


async def convergence_loop(
    task_type,
    inputs,
    world_res,
    emotion_res,
    critic_res,
    memory_res,
    session_id
):

    current_inputs = inputs
    final_output = None
    last_conflicts = None

    for round_id in range(MAX_ROUNDS):

        # =========================
        # 1. 冲突检测
        # =========================
        conflicts = detect_conflicts(current_inputs)

        # =========================
        # 2. 收敛判断
        # =========================
        if is_stable(conflicts):
            final_output = weighted_consensus(
                current_inputs,
                conflicts,
                task_type
            )
            break

        # =========================
        # 3. 生成中间修正版本
        # =========================
        final_output = weighted_consensus(
            current_inputs,
            conflicts,
            task_type
        )

        # =========================
        # 4. Reflection（关键）
        # =========================
        reflection = reflection_agent(
            "convergence_loop",
            final_output,
            critic_res,
            conflicts
        )

        # =========================
        # 5. 用反思修正输入（核心）
        # =========================
        current_inputs = {
            "executor": final_output,
            "critic": critic_res,
            "memory": memory_res,
            "world": world_res,
            "emotion": emotion_res,
            "reflection": reflection
        }

        last_conflicts = conflicts

    # =========================
    # 6. safety check
    # =========================
    if not check_output(final_output)["safe"]:
        final_output = safe_fallback()

    return final_output, last_conflicts

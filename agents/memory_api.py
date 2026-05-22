# agents/memory_api.py

from collections import defaultdict
import time

# =========================
# MEMORY STORE
# =========================
WORKING_MEMORY = defaultdict(list)


# =========================
# WRITE MEMORY
# =========================
def write_memory(session_id: str, text: str):
    WORKING_MEMORY[session_id].append({
        "text": text,
        "timestamp": time.time()
    })


# =========================
# READ MEMORY (v2.8统一接口)
# =========================
def get_memory_context(session_id: str, query: str = ""):
    """
    🧠 返回上下文（兼容 core.py）
    """

    memories = WORKING_MEMORY.get(session_id, [])[-10:]

    formatted = "\n".join([m["text"] for m in memories])

    return f"""
[MEMORY]
{formatted}

[QUERY]
{query}
"""

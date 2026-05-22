# agents/memory/memory_v2.py

import time

def write_memory(key: str, value: str):
    memory = get_memory_context()
    if len(memory) > 100:
        # Remove oldest entries to cap memory length
        memory.pop(0)
    memory.append({
        "text": value,
        "role": key,
        "timestamp": time.time()
    })

def get_memory_context():
    # Placeholder for actual memory context retrieval
    return []

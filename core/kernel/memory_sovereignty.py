class MemoryItem:
    def __init__(self, content, memory_type, task_type, score):
        self.content = content
        self.type = memory_type
        self.task_type = task_type
        self.importance = score
        self.access_count = 0
        self.last_access = 0

class MemoryManager:
    def __init__(self, hardening):
        self.store = {}
        self.hardening = hardening

    def write(self, key, value, actor):
        if actor != "kernel" and self.hardening.strict_isolation:
            return {"error": "memory_write_blocked"}
        return self._write_internal(key, value)

    def _write_internal(self, key, value):
        memory = self.store.get(key)
        if memory:
            memory.history.append(memory.value)
            memory.version += 1
            memory.value = value
        else:
            self.store[key] = MemoryItem(key, value, None, 0)
        return {"status": "ok"}

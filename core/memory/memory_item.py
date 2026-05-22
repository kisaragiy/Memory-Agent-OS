class MemoryItem:

    def __init__(self, content, memory_type, task_type, score):
        self.content = content
        self.type = memory_type
        self.task_type = task_type
        self.importance = score
        self.access_count = 0
        self.last_access = 0
        self.decay = 1.0

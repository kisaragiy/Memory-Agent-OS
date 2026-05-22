import asyncio
import uuid
from collections import deque

# =========================
# TASK STRUCTURE
# =========================

class Task:
    def __init__(self, user_input, task_type, session_id, priority=1):
        self.id = str(uuid.uuid4())
        self.user_input = user_input
        self.task_type = task_type
        self.session_id = session_id
        self.priority = priority


# =========================
# TASK QUEUE (控制队列)
# =========================

class TaskQueue:

    def __init__(self):
        self.queue = deque()

    def push(self, task: Task):
        self.queue.append(task)

    def pop(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def is_empty(self):
        return len(self.queue) == 0


# =========================
# AGENT SCHEDULER
# =========================

class AgentScheduler:

    def __init__(self):
        self.active_tasks = 0
        self.max_concurrency = 3  # 🧠 控制并发上限

    async def can_run(self):
        return self.active_tasks < self.max_concurrency

    async def acquire(self):
        self.active_tasks += 1

    async def release(self):
        self.active_tasks -= 1


# =========================
# SYSTEM STATE (控制中心)
# =========================

class SystemState:
    def __init__(self):
        self.status = "IDLE"
        self.current_task = None
        self.completed_tasks = 0

    def set_running(self):
        self.status = "RUNNING"

    def set_idle(self):
        self.status = "IDLE"

class TaskState:
    PLANNED = "PLANNED"

    def __init__(self):
        pass

    def get_task(self, task_id):
        request_action(task_id)

    def list_active_tasks(self):
        request_action({})

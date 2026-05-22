class Scheduler:
    def schedule(self, tasks):
        # priority + load balancing
        return sorted(tasks, key=lambda t: (t.priority, -t.load))

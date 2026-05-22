class MemoryStore:

    MAX_ITEMS = 100

    def __init__(self):
        self.data = []

    def add(self, item):

        self.data.append(item)

        # 超限 → 删除低价值
        if len(self.data) > self.MAX_ITEMS:
            self.data.sort(key=lambda x: x.importance * x.decay)
            self.data = self.data[-self.MAX_ITEMS:]

    def access(self, item):
        item.access_count += 1
        item.decay *= 1.05  # 越用越重要

    def decay_all(self):
        for item in self.data:
            item.decay *= 0.98

# core/agents/curriculum_manager.py

class CurriculumManager:

    def __init__(self):
        self.level = 1
        self.max_level = 5
        self.history = []

    def get_tasks(self):
        tasks = {
            1: [
                "解释什么是AI",
                "写一句话总结"
            ],
            2: [
                "写一个Python函数实现加法",
                "总结一段话并提取关键词"
            ],
            3: [
                "设计一个简单API",
                "解释递归并给出代码"
            ],
            4: [
                "实现一个小型系统架构设计",
                "多步骤推理问题"
            ],
            5: [
                "构建完整应用方案并给出代码结构",
                "复杂多工具协作任务"
            ]
        }
        return tasks.get(self.level, tasks[1])

    def update(self, score):
        self.history.append(score)

        if len(self.history) < 3:
            return

        avg_score = sum(self.history[-3:]) / 3

        # 防止一直刷简单任务
        if self.level == 1 and avg_score > 0.8:
            self.level = 2

        # 升级
        if avg_score > 0.75 and self.level < self.max_level:
            self.level += 1

        # 降级（防止卡死）
        elif avg_score < 0.4 and self.level > 1:
            self.level -= 1

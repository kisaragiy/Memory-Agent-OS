class TaskClassifier:

    def classify(self, input):

        text = input.lower()

        if any(k in text for k in ["写", "故事", "剧情"]):
            return "creative"

        if any(k in text for k in ["代码", "bug", "报错", "函数"]):
            return "coding"

        if any(k in text for k in ["解释", "为什么", "原理"]):
            return "qa"

        return "general"

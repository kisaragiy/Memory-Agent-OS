# core/kernel/narrative_engine.py

class NarrativeEngine:

    def __init__(self):
        self.story_threads = []

    def generate_narrative(self, world_state):

        """
        将世界状态转化为“叙事”
        """

        narrative = {
            "theme": None,
            "conflicts": [],
            "events": [],
            "tension": 0.0
        }

        # 简化叙事提取逻辑
        for event in world_state["timeline"]:

            if "conflict" in str(event):
                narrative["conflicts"].append(event)

            if "agent" in event:
                narrative["events"].append(event)

        # tension = 冲突密度
        narrative["tension"] = len(narrative["conflicts"]) / (len(world_state["timeline"]) + 1)

        return narrative

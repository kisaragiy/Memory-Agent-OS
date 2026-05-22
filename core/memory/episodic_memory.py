from datetime import datetime

class EpisodicMemory:
    def __init__(self):
        self.events = []

    def add_event(self, event: str, importance: float, entities: list):
        self.events.append({
            "event": event,
            "timestamp": datetime.now().timestamp(),
            "importance": importance,
            "entities": entities
        })

    def query_recent(self, top_k=5):
        return sorted(self.events, key=lambda x: x["timestamp"], reverse=True)[:top_k]

    def query_by_entity(self, entity):
        return [event for event in self.events if entity in event["entities"]]

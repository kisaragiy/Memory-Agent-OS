class CharacterGraph:

    def __init__(self):
        self.nodes = {}   # characters
        self.edges = {}   # relationships

    def add_character(self, name):
        self.nodes[name] = {
            "traits": [],
            "status": {}
        }

    def add_relation(self, a, b, relation_type, strength=1.0):
        self.edges[(a, b)] = {
            "type": relation_type,
            "strength": strength
        }

    def update_relation(self, a, b, delta):
        if (a, b) in self.edges:
            self.edges[(a, b)]["strength"] += delta

    def get_context(self, name):
        return {
            "node": self.nodes.get(name),
            "relations": {
                k: v for k, v in self.edges.items()
                if name in k
            }
        }

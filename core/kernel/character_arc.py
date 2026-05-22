# core/kernel/character_arc.py

class CharacterArcSystem:

    def __init__(self):
        self.arcs = {}

    def update_arc(self, character, event):

        if character not in self.arcs:
            self.arcs[character] = {
                "growth": 0,
                "conflict_history": []
            }

        if "conflict" in str(event):
            self.arcs[character]["growth"] += 1

        self.arcs[character]["conflict_history"].append(event)

    def get_arc(self, character):
        return self.arcs.get(character, None)

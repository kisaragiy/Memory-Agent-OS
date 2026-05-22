from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CharacterNode:
    name: str
    role: str = "character"
    traits: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)


class CharacterGraph:
    def __init__(self):
        self.nodes: Dict[str, CharacterNode] = {}

    def upsert(self, name: str, role: str = "character", traits: Optional[List[str]] = None):
        if name not in self.nodes:
            self.nodes[name] = CharacterNode(name=name, role=role, traits=traits or [])
        else:
            node = self.nodes[name]
            if traits:
                node.traits = list(set(node.traits + traits))

    def relate(self, a: str, b: str, relation: str):
        self.upsert(a)
        self.upsert(b)
        self.nodes[a].relationships[b] = relation
        inverse = {"敌对": "敌对", "恋人": "恋人", "同盟": "同盟"}.get(relation, "关联")
        self.nodes[b].relationships[a] = inverse

    def extract_from_text(self, text: str):
        import re

        for match in re.finditer(r"([\u4e00-\u9fff]{2,4})(?:和|与)([\u4e00-\u9fff]{2,4})(是|为)?(朋友|敌人|恋人|师徒|同盟)", text):
            self.relate(match.group(1), match.group(2), match.group(4))

        for match in re.finditer(r"主角[叫名是：:]?\s*([\u4e00-\u9fff]{2,6})", text):
            self.upsert(match.group(1), role="protagonist")

    def to_dict(self) -> Dict:
        return {
            name: {
                "role": n.role,
                "traits": n.traits,
                "relationships": n.relationships,
            }
            for name, n in self.nodes.items()
        }

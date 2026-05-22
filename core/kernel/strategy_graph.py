from typing import Dict

class StrategyGraph:

    def __init__(self):
        self.nodes = {}

    def add(self, node: 'StrategyNode'):
        self.nodes[node.name] = node

    def get_node(self, name: str) -> 'StrategyNode':
        return self.nodes.get(name)

    def connect(self, parent_name: str, child_name: str):
        parent = self.get_node(parent_name)
        child = self.get_node(child_name)
        if parent and child:
            parent.children.append(child)
            child.parents.append(parent)

    def remove(self, node: 'StrategyNode'):
        del self.nodes[node.name]
        for parent in node.parents:
            parent.children.remove(node)
        for child in node.children:
            child.parents.remove(node)

# core/kernel/execution_graph.py

class ExecutionNode:
    def __init__(self, name, func, deps=None):
        self.name = name
        self.func = func
        self.deps = deps or []
        self.result = None
        self.status = "pending"

class ExecutionGraph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node):
        self.nodes[node.name] = node

    def get_ready_nodes(self):
        return {
            'nodes': [n for n in self.nodes.values() if n.status == 'pending'],
            'type': 'execution_graph'
        }

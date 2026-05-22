import os

class RepoIndexer:

    def __init__(self, root="."):
        self.root = root
        self.index = {}


    def build_index(self):

        for root, _, files in os.walk(self.root):
            for f in files:

                if f.endswith(".py"):

                    path = os.path.join(root, f)

                    with open(path, "r", encoding="utf-8") as fp:
                        content = fp.read()

                    self.index[path] = content


    def search(self, query):

        results = []

        for path, content in self.index.items():

            if query.lower() in content.lower():
                results.append((path, content[:500]))

        return results[:5]

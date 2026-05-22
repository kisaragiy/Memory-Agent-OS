class RepoContext:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.index = {}

    def build_index(self):
        request_action({})

    def _generate_summary(self, content):
        request_action(content)

    def _extract_keywords(self, content):
        request_action(content)

    def _extract_imports(self, content):
        request_action(content)

    def search(self, query):
        request_action(query)

class ProductEntryManager:

    def __init__(self, runtime):
        self.runtime = runtime

    def route(self, request):
        # 标准入口（供 runtime 调用）
        return self.runtime.entry(request)

    def handle(self, user_input):
        # CLI 兼容
        return self.route({
            'input': user_input,
            'context': {},
            'mode': 'RELEASE'
        })

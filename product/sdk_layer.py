class AgentSDK:
    def __init__(self, api_key, gateway):
        self.api_key = api_key
        self.gateway = gateway

    def run(self, input):
        return self.gateway.handle_request({
            "input": input,
            "api_key": self.api_key
        })

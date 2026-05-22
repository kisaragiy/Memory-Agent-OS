from typing import Dict

class APIGateway:
    def validate(self, request: Dict) -> Dict:
        # 只做结构检查，不做 required_fields 校验
        if not isinstance(request, dict):
            raise ValueError("Request must be a dictionary")
        return request

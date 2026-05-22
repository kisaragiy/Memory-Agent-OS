"""
Backward-compatible dev entry — production use: python -m agent_service
"""

import uvicorn
from agent_service.app import app
from agent_service.settings import SETTINGS

if __name__ == "__main__":
    uvicorn.run(app, host=SETTINGS.host, port=8000)

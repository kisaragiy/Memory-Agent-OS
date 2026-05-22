import uvicorn

from agent_service.settings import SETTINGS


def main():
    uvicorn.run(
        "agent_service.app:app",
        host=SETTINGS.host,
        port=SETTINGS.port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()

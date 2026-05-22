"""
Optional Windows Service host (pywin32).

Install: pip install pywin32
Register: python agent_service/windows_service.py install
Start:    python agent_service/windows_service.py start

Prefer scripts/windows/install_agent_service.ps1 (NSSM) when pywin32 is unavailable.
"""

from __future__ import annotations

import os
import sys

# Project root on sys.path when run as script
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _run_uvicorn():
    import uvicorn

    from agent_service.settings import SETTINGS

    uvicorn.run(
        "agent_service.app:app",
        host=SETTINGS.host,
        port=SETTINGS.port,
        log_level="info",
    )


try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager

    class MemoryAgentService(win32serviceutil.ServiceFramework):
        _svc_name_ = "MemoryAgentOS"
        _svc_display_name_ = "Memory Agent OS"
        _svc_description_ = "Agent OS HTTP runtime (single kernel path)"

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.stop_event)

        def SvcDoRun(self):
            import threading

            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ""),
            )
            threading.Thread(target=_run_uvicorn, daemon=True).start()
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

    if __name__ == "__main__":
        if len(sys.argv) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(MemoryAgentService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            win32serviceutil.HandleCommandLine(MemoryAgentService)

except ImportError:

    if __name__ == "__main__":
        print("pywin32 not installed. Use: pip install pywin32")
        print("Or: scripts/windows/install_agent_service.ps1")
        sys.exit(1)

"""Production service settings (env overrides)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class ServiceSettings:
    host: str = "0.0.0.0"
    port: int = 8787
    default_agent_id: str = "web-agent"
    control_mode: str = "user"
    enable_autonomous: bool = False
    enable_live: bool = False
    enable_windows_desktop: bool = False
    static_dir: str = ""
    react_dist_dir: str = ""

    @classmethod
    def from_env(cls) -> "ServiceSettings":
        root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        static = os.environ.get(
            "AGENT_STATIC_DIR", os.path.join(root, "web")
        )
        react_dist = os.environ.get(
            "AGENT_REACT_DIST", os.path.join(root, "web", "frontend", "dist")
        )
        return cls(
            host=os.environ.get("AGENT_SERVICE_HOST", "0.0.0.0"),
            port=int(os.environ.get("AGENT_SERVICE_PORT", "8787")),
            default_agent_id=os.environ.get("AGENT_DEFAULT_ID", "web-agent"),
            control_mode=os.environ.get("AGENT_CONTROL_MODE", "user"),
            enable_autonomous=os.environ.get("AGENT_AUTONOMOUS", "")
            in ("1", "true", "yes"),
            enable_live=os.environ.get("GUARDED_UI_LIVE", "")
            in ("1", "true", "yes"),
            enable_windows_desktop=_default_windows_desktop(),
            static_dir=static,
            react_dist_dir=react_dist,
        )


def _default_windows_desktop() -> bool:
    explicit = os.environ.get("AGENT_WINDOWS_DESKTOP", "").strip().lower()
    if explicit in ("0", "false", "no"):
        return False
    if explicit in ("1", "true", "yes"):
        return True
    try:
        with open("/proc/version", encoding="utf-8", errors="ignore") as f:
            if "microsoft" in f.read().lower():
                return True
    except OSError:
        pass
    return os.name == "nt"


def _patch_settings_from_env(s: ServiceSettings) -> ServiceSettings:
    if not s.enable_windows_desktop and _default_windows_desktop():
        s.enable_windows_desktop = True
        if not os.environ.get("AUTONOMOUS_CAPTURE"):
            os.environ.setdefault("AUTONOMOUS_CAPTURE", "1")
        if not os.environ.get("USE_VISION_OBSERVER"):
            os.environ.setdefault("USE_VISION_OBSERVER", "1")
    return s


SETTINGS = _patch_settings_from_env(ServiceSettings.from_env())

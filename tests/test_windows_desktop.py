"""Windows desktop bridge — parse bounds + env gates."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.platform.windows_desktop import WindowsDesktop


def test_parse_bounds_dict():
    b = WindowsDesktop.parse_bounds({"x": 10, "y": 20, "w": 100, "h": 40})
    assert b == {"x": 10, "y": 20, "w": 100, "h": 40}


def test_parse_bounds_string():
    b = WindowsDesktop.parse_bounds("100,200,50,30")
    assert b["x"] == 100 and b["w"] == 50


def test_resolve_point_center():
    x, y = WindowsDesktop._resolve_point({"x": 0, "y": 0, "w": 200, "h": 100})
    assert x == 100 and y == 50

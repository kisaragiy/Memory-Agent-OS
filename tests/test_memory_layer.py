"""Memory layer persistence and policy smoke tests."""

import shutil
from pathlib import Path

from core.memory.memory_layer import MemoryLayer
from core.memory.types import MemoryKind


def test_remember_dedupe(tmp_path, monkeypatch):
    base = tmp_path / "agents"
    layer = MemoryLayer()
    layer._store = __import__(
        "core.memory.persistent_store", fromlist=["PersistentStore"]
    ).PersistentStore(str(base))
    layer._records_cache.clear()
    aid = "test-agent"
    r1 = layer.remember(aid, "用户喜欢恐怖小说", MemoryKind.PREFERENCE)
    r2 = layer.remember(aid, "用户喜欢恐怖小说", MemoryKind.PREFERENCE)
    assert r1.id == r2.id
    assert r2.metadata.get("access_count", 0) >= 1


def test_episodes_persist(tmp_path):
    from core.memory.persistent_store import PersistentStore
    from core.memory.types import Episode

    store = PersistentStore(str(tmp_path / "agents"))
    ep = Episode(
        trace_id="t1",
        user_input="hi",
        plan_summary="chat",
        status="success",
        assistant_output="hello",
    )
    store.save_episodes("a1", [ep])
    loaded = store.load_episodes("a1")
    assert len(loaded) == 1
    assert loaded[0].user_input == "hi"

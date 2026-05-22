"""
Production FastAPI application — Agent OS HTTP surface.

All execution flows through AgentOSRuntime.entry() only.
Control layer enforces user vs developer presentation at the boundary.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent_service.runtime_manager import RUNTIME_MANAGER
from agent_service.settings import SETTINGS
from core.control import PresentationPolicy, SESSION_CONTROLS, RuntimeControl
from core.control.model_policy import ModelPolicy
from core.control.output_filter import OutputFilter
from core.control.memory_control import MemoryControl, MemoryGovernanceError
from core.memory import get_memory_layer
from core.runtime import observability


class RunRequest(BaseModel):
    input: str
    session_id: Optional[str] = None
    mode: Optional[str] = Field(
        None, description="user | developer | debug (overrides developer flag)"
    )
    developer: bool = False
    trace: Optional[bool] = None
    user_confirmed: bool = False
    demo: bool = False
    autonomous_session: bool = False
    max_autonomous_steps: int = 6


class RememberRequest(BaseModel):
    fact: str
    session_id: Optional[str] = None


class MemoryMutateRequest(BaseModel):
    """Governed memory intent — not CRUD."""
    session_id: Optional[str] = None
    op: str = "update_memory"
    target: str = "semantic"
    action: str = "merge"
    fact: str = ""
    record_id: Optional[str] = None
    kind: str = "fact"
    snapshot_id: Optional[str] = None
    reason: str = ""
    inject_test: bool = False


class ControlUpdateRequest(BaseModel):
    session_id: Optional[str] = None
    mode: Optional[str] = None
    trace_enabled: Optional[bool] = None
    demo: Optional[bool] = None


def _session_id(request_session: Optional[str]) -> str:
    return request_session or SETTINGS.default_agent_id


def create_app() -> FastAPI:
    app = FastAPI(
        title="Memory Agent OS",
        version="1.1.0",
        description="Production API — single kernel, control-layer presentation",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    async def health():
        from core.platform.windows_desktop import WindowsDesktop

        return {
            "status": "ok",
            "service": "memory-agent-os",
            "default_agent": SETTINGS.default_agent_id,
            "control_mode_default": SETTINGS.control_mode,
            "autonomous": SETTINGS.enable_autonomous,
            "live": SETTINGS.enable_live,
            "windows_desktop": SETTINGS.enable_windows_desktop,
            "desktop": {
                "wsl": WindowsDesktop.is_wsl(),
                "capture_enabled": WindowsDesktop.capture_enabled(),
                "automation_available": WindowsDesktop.automation_available(),
            },
            "valid_modes": list(RuntimeControl.VALID_MODES),
        }

    @app.get("/api/desktop/screenshot")
    async def desktop_screenshot_preview():
        """
        Developer diagnostic — capture host Windows desktop and return PNG.
        Open http://127.0.0.1:8787/api/desktop/screenshot in browser to verify vision input.
        """
        from core.platform.windows_desktop import WindowsDesktop

        path, meta = WindowsDesktop.capture_screenshot()
        if not path:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "message": "截屏失败",
                    "meta": meta,
                    "hint": "Windows: 运行 scripts/windows/Verify-DesktopCapture.ps1",
                },
            )
        return FileResponse(
            path,
            media_type="image/png",
            filename="memory_chat_desktop.png",
            headers={"X-Capture-Meta": str(meta.get("source", ""))},
        )

    @app.get("/api/desktop/stream")
    async def desktop_live_stream(
        interval_ms: int = Query(1500, ge=500, le=10000),
    ):
        """
        Phase 5 — MJPEG-like live desktop preview (multipart/x-mixed-replace).
        Use in <img src="/api/desktop/stream"> in developer UI.
        """
        from core.platform.windows_desktop import WindowsDesktop

        boundary = b"frame"

        async def frame_generator():
            while True:
                path, meta = await asyncio.to_thread(
                    WindowsDesktop.capture_screenshot
                )
                if path and os.path.isfile(path):
                    with open(path, "rb") as f:
                        payload = f.read()
                    yield b"--" + boundary + b"\r\n"
                    yield b"Content-Type: image/png\r\n\r\n"
                    yield payload + b"\r\n"
                else:
                    stub = (
                        b'{"status":"no_frame","meta":'
                        + json.dumps(meta or {}).encode()
                        + b"}"
                    )
                    yield b"--" + boundary + b"\r\n"
                    yield b"Content-Type: application/json\r\n\r\n"
                    yield stub + b"\r\n"
                await asyncio.sleep(interval_ms / 1000.0)

        return StreamingResponse(
            frame_generator(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
        )

    @app.post("/api/autonomous/run")
    async def autonomous_run(request: RunRequest):
        """Phase 5 — closed-loop autonomous session (single kernel)."""
        sid = _session_id(request.session_id)
        runtime = RUNTIME_MANAGER.get(
            sid,
            mode=request.mode or RuntimeControl.DEVELOPER,
            developer=True,
            trace=request.trace,
        )
        os.environ.setdefault("AGENT_WINDOWS_DESKTOP", "1")
        os.environ.setdefault("AUTONOMOUS_CAPTURE", "1")
        result = runtime.run_autonomous_session(
            request.input,
            max_steps=request.max_autonomous_steps,
            user_confirmed=request.user_confirmed or True,
        )
        control = runtime.control
        flags = ModelPolicy.resolve_flags(control.mode)
        payload = result.to_dict()
        return OutputFilter.filter_http_response(payload, flags)

    @app.post("/api/autonomous/stream")
    async def autonomous_stream(request: RunRequest):
        sid = _session_id(request.session_id)
        runtime = RUNTIME_MANAGER.get(
            sid,
            mode=request.mode or RuntimeControl.DEVELOPER,
            developer=True,
            trace=request.trace,
        )
        control = runtime.control
        os.environ.setdefault("AGENT_WINDOWS_DESKTOP", "1")

        async def event_stream():
            def emit(step: str, data: Dict[str, Any]):
                ev = PresentationPolicy.sanitize_stream_event(control, step, data)
                return json.dumps(ev, ensure_ascii=False) + "\n"

            yield emit("started", {"goal": request.input, "phase": "5"})
            try:
                for event in runtime.iter_autonomous_session(
                    request.input,
                    max_steps=request.max_autonomous_steps,
                    user_confirmed=request.user_confirmed or True,
                ):
                    et = event.get("type")
                    if et == "progress":
                        yield emit(
                            "desktop_observe",
                            {
                                "label": event.get("message", "处理中…"),
                                "step_index": event.get("step_index"),
                            },
                        )
                    elif et == "step":
                        rec = event.get("record")
                        rd = rec.to_dict() if hasattr(rec, "to_dict") else rec
                        yield emit("autonomous_step", rd or {})
                    elif et == "complete":
                        yield emit(
                            "execution_complete",
                            {
                                "result": event.get("final_output"),
                                "status": event.get("status"),
                            },
                        )
                        return
                    elif et == "error":
                        yield emit("error", {"message": event.get("error")})
                        return
            except Exception as exc:
                yield emit("error", {"message": str(exc)})

        return StreamingResponse(event_stream(), media_type="application/x-ndjson")

    @app.get("/api/control")
    async def get_control(session_id: Optional[str] = Query(None)):
        sid = _session_id(session_id)
        sc = SESSION_CONTROLS.get(sid)
        rt_control = RUNTIME_MANAGER.control_for(sid)
        return {
            "session_id": sid,
            "session": {
                "mode": sc.mode,
                "trace_enabled": sc.trace_enabled,
                "demo": sc.demo,
            },
            "runtime": rt_control.to_dict(),
        }

    @app.post("/api/control")
    async def update_control(body: ControlUpdateRequest):
        sid = _session_id(body.session_id)
        try:
            sc = SESSION_CONTROLS.set(
                sid,
                mode=body.mode,
                trace_enabled=body.trace_enabled,
                demo=body.demo,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if body.mode:
            RUNTIME_MANAGER.get(sid, mode=body.mode, trace=body.trace_enabled)
        return {
            "session_id": sid,
            "session": {
                "mode": sc.mode,
                "trace_enabled": sc.trace_enabled,
                "demo": sc.demo,
            },
        }

    @app.post("/api/run")
    async def run_agent(request: RunRequest):
        sid = _session_id(request.session_id)
        control = SESSION_CONTROLS.get(sid).to_runtime_control()
        if request.mode:
            control = RuntimeControl.from_request(
                mode=request.mode, developer=request.developer, trace=request.trace
            )

        if request.demo or SESSION_CONTROLS.get(sid).demo:
            return PresentationPolicy.demo_response(request.input, sid)

        runtime = RUNTIME_MANAGER.get(
            sid,
            mode=request.mode,
            developer=request.developer,
            trace=request.trace,
        )
        control = runtime.control
        try:
            if request.autonomous_session:
                os.environ.setdefault("AGENT_WINDOWS_DESKTOP", "1")
                raw = runtime.run_autonomous_session(
                    request.input,
                    max_steps=request.max_autonomous_steps,
                    user_confirmed=request.user_confirmed or True,
                ).to_dict()
            else:
                raw = runtime.entry(
                    request.input,
                    user_confirmed=request.user_confirmed,
                )
            trace_id = None
            if isinstance(raw, dict):
                trace_id = raw.get("trace_id")
            flags = ModelPolicy.resolve_flags(control.mode)
            wrapped = PresentationPolicy.wrap_run_response(
                control, raw, session_id=sid, trace_id=trace_id
            )
            if flags.show_trace and trace_id:
                wrapped["trace"] = observability._hub.get_trace(trace_id)
            return OutputFilter.filter_http_response(wrapped, flags, trace_id=trace_id)
        except Exception as exc:
            detail = PresentationPolicy.http_error_detail(control, exc)
            code = 500 if control.is_user_mode() else 500
            raise HTTPException(status_code=code, detail=detail) from exc

    @app.post("/api/stream")
    async def stream_agent(request: RunRequest):
        sid = _session_id(request.session_id)
        runtime = RUNTIME_MANAGER.get(
            sid,
            mode=request.mode,
            developer=request.developer,
            trace=request.trace,
        )
        control = runtime.control

        async def event_stream():
            def emit(step: str, data: Dict[str, Any]):
                ev = PresentationPolicy.sanitize_stream_event(control, step, data)
                return json.dumps(ev, ensure_ascii=False) + "\n"

            yield emit("started", {"input": request.input})

            if request.demo or SESSION_CONTROLS.get(sid).demo:
                demo = PresentationPolicy.demo_response(request.input, sid)
                yield emit(
                    "execution_complete",
                    {"result": demo},
                )
                return

            try:
                if request.autonomous_session:
                    os.environ.setdefault("AGENT_WINDOWS_DESKTOP", "1")
                    for event in runtime.iter_autonomous_session(
                        request.input,
                        max_steps=request.max_autonomous_steps,
                        user_confirmed=request.user_confirmed or True,
                    ):
                        et = event.get("type")
                        if et == "progress":
                            yield emit(
                                "desktop_observe",
                                {"label": event.get("message", "")},
                            )
                        elif et == "step":
                            rec = event.get("record")
                            yield emit(
                                "autonomous_step",
                                rec.to_dict() if hasattr(rec, "to_dict") else rec,
                            )
                        elif et == "complete":
                            yield emit(
                                "execution_complete",
                                {"result": event.get("final_output")},
                            )
                            return
                        elif et == "error":
                            yield emit("error", {"message": event.get("error")})
                            return
                else:
                    raw = runtime.entry(
                        request.input,
                        user_confirmed=request.user_confirmed,
                    )
                    yield emit("execution_complete", {"result": raw})
            except Exception as exc:
                err = control.format_error(exc)
                yield emit("error", err if isinstance(err, dict) else {"error": str(exc)})

        return StreamingResponse(
            event_stream(),
            media_type="application/x-ndjson",
        )

    @app.get("/api/memory")
    async def get_memory(
        agent_id: Optional[str] = Query(None),
        mode: Optional[str] = Query(None),
    ):
        aid = agent_id or SETTINGS.default_agent_id
        control = RUNTIME_MANAGER.control_for(aid)
        if mode:
            control = RuntimeControl(mode=mode)
        layer = get_memory_layer()
        layer.ensure_agent_ready(aid)
        snapshot = layer.export_snapshot(aid)
        if control.is_user_mode():
            return {
                "agent_id": aid,
                "memory": {
                    "facts": [
                        {"content": f["content"]}
                        for f in snapshot.get("facts", [])
                    ],
                    "episode_count": snapshot.get("episode_count", 0),
                },
            }
        return {"agent_id": aid, "memory": snapshot}

    @app.get("/api/memory/search")
    async def search_memory(
        q: str = Query(..., min_length=1),
        agent_id: Optional[str] = Query(None),
        mode: Optional[str] = Query(None),
    ):
        aid = agent_id or SETTINGS.default_agent_id
        control = RUNTIME_MANAGER.control_for(aid)
        if mode:
            control = RuntimeControl(mode=mode)
        if control.is_user_mode():
            raise HTTPException(
                status_code=403,
                detail="语义检索仅在开发者模式可用",
            )
        layer = get_memory_layer()
        ctx = layer.build_context(aid, q)
        return {
            "agent_id": aid,
            "query": q,
            "retrieved": ctx.get("retrieved_memories") or [],
        }

    @app.post("/api/memory/remember")
    async def remember_fact(request: RememberRequest):
        aid = _session_id(request.session_id)
        runtime = RUNTIME_MANAGER.get(aid)
        try:
            out = runtime.dispatch_memory_mutation(
                MemoryControl.remember_intent(request.fact)
            )
        except MemoryGovernanceError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        inner = (out.get("result") or {}) if isinstance(out.get("result"), dict) else {}
        return {
            "id": inner.get("id", ""),
            "content": inner.get("content", request.fact),
            "agent_id": aid,
            "trace_id": out.get("trace_id"),
            "mutation": out.get("mutation"),
        }

    @app.post("/api/memory/mutate")
    async def mutate_memory(request: MemoryMutateRequest):
        aid = _session_id(request.session_id)
        runtime = RUNTIME_MANAGER.get(aid, mode="developer")
        if runtime.control.is_user_mode():
            raise HTTPException(
                status_code=403,
                detail="Memory mutation requires developer or debug mode",
            )
        intent = {
            "op": request.op,
            "target": request.target,
            "action": request.action,
            "fact": request.fact,
            "record_id": request.record_id,
            "kind": request.kind,
            "snapshot_id": request.snapshot_id,
            "reason": request.reason,
            "inject_test": request.inject_test,
        }
        try:
            return runtime.dispatch_memory_mutation(intent)
        except MemoryGovernanceError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/memory/mutations")
    async def list_memory_mutations(
        agent_id: Optional[str] = Query(None),
        mode: Optional[str] = Query("developer"),
    ):
        aid = agent_id or SETTINGS.default_agent_id
        control = RuntimeControl(mode=mode or "developer")
        if control.is_user_mode():
            raise HTTPException(status_code=403, detail="Developer mode required")
        return {
            "agent_id": aid,
            "mutations": MemoryControl.list_mutation_traces(aid),
        }

    @app.post("/api/memory/snapshot")
    async def create_memory_snapshot(
        agent_id: Optional[str] = Query(None),
        mode: Optional[str] = Query("developer"),
    ):
        aid = agent_id or SETTINGS.default_agent_id
        runtime = RUNTIME_MANAGER.get(aid, mode=mode or "developer")
        if runtime.control.is_user_mode():
            raise HTTPException(status_code=403, detail="Developer mode required")
        import uuid

        sid = str(uuid.uuid4())[:8]
        return runtime.dispatch_memory_mutation(
            {
                "op": "update_memory",
                "target": "semantic",
                "action": "snapshot",
                "snapshot_id": sid,
            }
        )

    @app.get("/api/memory/snapshots")
    async def list_memory_snapshots(
        agent_id: Optional[str] = Query(None),
        mode: Optional[str] = Query("developer"),
    ):
        aid = agent_id or SETTINGS.default_agent_id
        control = RuntimeControl(mode=mode or "developer")
        if control.is_user_mode():
            raise HTTPException(status_code=403, detail="Developer mode required")
        layer = get_memory_layer()
        return {"agent_id": aid, "snapshots": layer.list_snapshots(aid)}

    @app.delete("/api/memory/session")
    async def clear_session_cache(agent_id: str = Query(...)):
        RUNTIME_MANAGER.invalidate(agent_id)
        return {"cleared": agent_id}

    @app.get("/api/tools")
    async def get_tools(
        agent_id: Optional[str] = Query(None),
        mode: Optional[str] = Query(None),
    ):
        aid = agent_id or SETTINGS.default_agent_id
        runtime = RUNTIME_MANAGER.get(aid, mode=mode)
        names = runtime.tool_registry.list()
        if runtime.control.is_user_mode():
            return {"tools": [{"name": n} for n in names]}
        return {"tools": names}

    @app.get("/api/trace/{session_id}")
    async def get_trace(
        session_id: str,
        mode: Optional[str] = Query(None),
    ):
        control = RuntimeControl(mode=mode) if mode else RUNTIME_MANAGER.control_for(session_id)
        if control.is_user_mode():
            raise HTTPException(
                status_code=403,
                detail={"status": "error", "message": "普通模式下无法查看执行链。"},
            )
        traces = observability._hub.traces.get(session_id, [])
        if not traces:
            for key, steps in observability._hub.traces.items():
                if key.startswith(session_id):
                    traces = steps
                    break
        return {
            "session_id": session_id,
            "trace": traces,
            "graph": observability._hub.export_graph(session_id),
        }

    @app.get("/api/replay/{trace_id}")
    async def replay_trace(
        trace_id: str,
        mode: Optional[str] = Query("developer"),
    ):
        control = RuntimeControl(mode=mode)
        if control.is_user_mode():
            raise HTTPException(status_code=403, detail="Replay requires developer mode")
        steps = observability._hub.get_trace(trace_id)
        return {"trace_id": trace_id, "steps": steps}

    # Legacy aliases
    @app.post("/run")
    async def run_legacy(request: RunRequest):
        return await run_agent(request)

    @app.get("/memory")
    async def memory_legacy(agent_id: Optional[str] = Query(None)):
        return await get_memory(agent_id)

    @app.post("/memory/remember")
    async def remember_legacy(request: RememberRequest):
        return await remember_fact(request)

    @app.get("/tools")
    async def tools_legacy(agent_id: Optional[str] = Query(None)):
        return await get_tools(agent_id)

    react_dist = SETTINGS.react_dist_dir
    if os.path.isdir(react_dist):
        app.mount("/app", StaticFiles(directory=react_dist, html=True), name="react_app")

        @app.get("/")
        async def root_react():
            return RedirectResponse(url="/app/")

    static_dir = SETTINGS.static_dir
    if os.path.isdir(static_dir):
        app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="legacy_ui")

        if not os.path.isdir(react_dist):

            @app.get("/")
            async def root_legacy():
                index = os.path.join(static_dir, "index.html")
                if os.path.isfile(index):
                    return FileResponse(index)
                return {"message": "Agent OS API", "ui": "/ui/index.html"}

    if not os.path.isdir(react_dist) and not os.path.isdir(static_dir):

        @app.get("/")
        async def root_api_only():
            return {"message": "Memory Agent OS API", "docs": "/docs"}

    return app


app = create_app()

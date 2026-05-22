# api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging
from core.kernel.runtime import UnifiedKernelRuntime

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# ===== Kernel 引入 =====
try:
    SINGLE_KERNEL = UnifiedKernelRuntime(chroma_client=None)  # Assuming chroma_client is not needed for initialization
except Exception as e:
    logging.error(f"❌ Kernel load failed: {e}")
    raise HTTPException(status_code=503, detail="Kernel load failed")

# ===== Request Models =====

class ChatRequest(BaseModel):
    message: str


# ===== Health =====

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/kernel/health")
async def kernel_health():
    try:
        result = SINGLE_KERNEL.run({"input_text": "health_check", "plan": {}})
        return {
            "kernel": "active" if "trace_id" in result else "inactive",
            "trace": result.get("trace", {})
        }
    except Exception as e:
        logging.error(e)
        return {"kernel": "error", "detail": str(e)}


# ===== Chat（唯一入口） =====

@app.post("/chat")
async def chat(data: ChatRequest):
    try:
        result = SINGLE_KERNEL.entry({
            "type": "chat",
            "input": data.message
        })
        return {"reply": result}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


# ===== Debug API（必须）=====

@app.get("/tools/stats")
async def tool_stats():
    return SINGLE_KERNEL.tool_router.learning.tool_scores


# ===== 启动 =====

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

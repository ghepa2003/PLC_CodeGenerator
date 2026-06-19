import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from layers.orchestration import Orchestrator
import uvicorn
from config import PORT, HOST, CORS_ORIGIN

app = FastAPI(title="PLC Code Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

class GenerateRequest(BaseModel):
    input_nl: str
    plc_type: str = "allen_bradley"
    safety_level: str = "medium"

from agents.base_agent import BaseAgent

@app.get("/api/debug")
async def debug_endpoint():
    import os
    key = os.getenv("OPENROUTER_API_KEY", "")
    masked_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "INVALID_OR_MISSING"
    
    agent = BaseAgent("test", "openrouter/free")
    
    test_result = "Not Tested"
    error_msg = None
    
    if not agent.is_mock:
        try:
            response = await agent.client.chat.completions.create(
                model="openrouter/free",
                messages=[{"role": "user", "content": "Say 'hello'"}],
                temperature=0.2
            )
            test_result = response.choices[0].message.content
        except Exception as e:
            test_result = "ERROR"
            error_msg = str(e)
            import traceback
            error_msg += " " + traceback.format_exc()

    return {
        "is_mock_mode": agent.is_mock,
        "key_preview": masked_key,
        "test_call_result": test_result,
        "error_details": error_msg
    }

@app.post("/api/generate-ladder")
async def generate_ladder_endpoint(req: GenerateRequest):
    try:
        result = await orchestrator.execute_workflow(
            input_nl=req.input_nl,
            plc_type=req.plc_type,
            safety_level=req.safety_level
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)

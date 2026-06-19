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

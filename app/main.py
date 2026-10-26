"""FastAPI app: serves the page and the JSON API. Keeps nothing between requests."""
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.errors import PipelineError
from app.pipeline import run_pipeline
from app.providers import get_provider

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
STATUS = {"cannot_read": 422, "unsupported_in_mode": 422, "provider_error": 502}

app = FastAPI(title="Communications Interpreter")


@app.exception_handler(PipelineError)
async def pipeline_error_handler(_, exc: PipelineError):
    return JSONResponse({"code": exc.code}, status_code=STATUS.get(exc.code, 500))


@app.get("/api/config")
async def get_config():
    provider = config.provider_name()
    accepts = ["pdf", "txt"] + (["png", "jpg"] if provider == "gemini" else [])
    return {"provider": provider, "accepts": accepts}


@app.post("/api/explain")
async def explain(file: UploadFile = File(...)):
    data = await file.read()
    # The pipeline makes blocking network calls, so run it off the event loop.
    result = await run_in_threadpool(run_pipeline, file.filename or "", data, get_provider())
    return result.model_dump()


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

"""FastAPI proxy that turns a photo + text instruction into a ComfyUI edit job.

Endpoints
---------
POST /jobs              multipart (image, prompt) -> JobInfo (job_id)
GET  /jobs/{job_id}     -> JobInfo (status + progress)
GET  /jobs/{job_id}/image -> the edited PNG once completed
GET  /health            -> simple readiness probe
"""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .comfy_client import ComfyExecutionError, ComfyUIClient
from .config import settings
from .jobs import Job, store
from .models import JobInfo, JobStatus
from .workflow import build_workflow

app = FastAPI(title="ComfyUI Image Edit Proxy", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

comfy = ComfyUIClient(settings.comfyui_url)

UPLOAD_DIR = Path(settings.upload_dir)
OUTPUT_DIR = Path(settings.output_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_IMAGE_BYTES = 25 * 1024 * 1024  # 25 MB upload guard.


def _to_info(job: Job) -> JobInfo:
    return JobInfo(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        prompt=job.prompt,
        error=job.error,
        image_available=bool(job.output_path),
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "comfyui_url": settings.comfyui_url}


@app.post("/jobs", response_model=JobInfo)
async def create_job(
    prompt: str = Form(...),
    image: UploadFile = File(...),
) -> JobInfo:
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt must not be empty")

    contents = await image.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded image is empty")
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image is too large (max 25 MB)")

    job_id = uuid.uuid4().hex
    job = store.create(job_id, prompt.strip())
    filename = image.filename or "input.png"
    asyncio.create_task(_run_job(job_id, prompt.strip(), contents, filename))
    return _to_info(job)


@app.get("/jobs/{job_id}", response_model=JobInfo)
async def get_job(job_id: str) -> JobInfo:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return _to_info(job)


@app.get("/jobs/{job_id}/image")
async def get_job_image(job_id: str) -> FileResponse:
    job = store.get(job_id)
    if job is None or not job.output_path:
        raise HTTPException(status_code=404, detail="Image not ready")
    return FileResponse(job.output_path, media_type="image/png")


async def _run_job(job_id: str, prompt: str, image_bytes: bytes, filename: str) -> None:
    """Background task: upload, queue, track, and store the edited image."""
    client_id = uuid.uuid4().hex
    try:
        store.update(job_id, status=JobStatus.running, progress=0)

        image_name = await comfy.upload_image(image_bytes, f"{job_id}_{filename}")
        workflow = build_workflow(prompt, image_name)
        prompt_id = await comfy.queue_prompt(workflow, client_id)

        def on_progress(pct: int) -> None:
            store.update(job_id, progress=max(0, min(100, pct)))

        try:
            await asyncio.wait_for(
                comfy.track_progress(prompt_id, client_id, on_progress),
                timeout=settings.result_timeout,
            )
        except ComfyExecutionError:
            raise
        except Exception:
            # WebSocket progress is best-effort; correctness comes from history below.
            pass

        entry = await comfy.wait_for_history(prompt_id)
        image_info = _find_output_image(entry.get("outputs", {}))
        if image_info is None:
            raise ComfyExecutionError("ComfyUI did not return an output image")

        data = await comfy.fetch_image(
            image_info["filename"],
            image_info.get("subfolder", ""),
            image_info.get("type", "output"),
        )
        out_path = OUTPUT_DIR / f"{job_id}.png"
        out_path.write_bytes(data)
        store.update(
            job_id,
            status=JobStatus.completed,
            progress=100,
            output_path=str(out_path),
        )
    except Exception as exc:  # noqa: BLE001 - surface any failure to the client
        store.update(job_id, status=JobStatus.failed, error=str(exc))


def _find_output_image(outputs: dict) -> dict | None:
    for node_output in outputs.values():
        images = node_output.get("images")
        if images:
            return images[0]
    return None

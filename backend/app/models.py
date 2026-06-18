"""Pydantic models describing the API request/response shapes."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class JobInfo(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = 0
    prompt: str
    error: str | None = None
    image_available: bool = False

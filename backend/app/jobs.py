"""A tiny thread-safe, in-memory store for tracking edit jobs.

This is intentionally simple (no database) so the project runs with zero
infrastructure. Jobs live only for the lifetime of the server process.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass

from .models import JobStatus


@dataclass
class Job:
    job_id: str
    prompt: str
    status: JobStatus = JobStatus.queued
    progress: int = 0
    error: str | None = None
    output_path: str | None = None


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str, prompt: str) -> Job:
        with self._lock:
            job = Job(job_id=job_id, prompt=prompt)
            self._jobs[job_id] = job
            return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **fields) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            for key, value in fields.items():
                setattr(job, key, value)
            return job


store = JobStore()

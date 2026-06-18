"""Async client for talking to a ComfyUI server over its HTTP + WebSocket API."""
from __future__ import annotations

import asyncio
import json
from typing import Callable

import httpx
import websockets


class ComfyExecutionError(RuntimeError):
    """Raised when ComfyUI reports an error while executing a workflow."""


class ComfyUIClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.ws_url = (
            self.base_url.replace("https://", "wss://").replace("http://", "ws://")
        )

    async def upload_image(self, file_bytes: bytes, filename: str) -> str:
        """Upload an image to ComfyUI's input folder and return its stored name."""
        files = {"image": (filename, file_bytes, "application/octet-stream")}
        data = {"overwrite": "true"}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/upload/image", files=files, data=data
            )
            resp.raise_for_status()
            info = resp.json()
        name = info["name"]
        subfolder = info.get("subfolder")
        return f"{subfolder}/{name}" if subfolder else name

    async def queue_prompt(self, workflow: dict, client_id: str) -> str:
        """Submit a workflow for execution and return its prompt_id."""
        payload = {"prompt": workflow, "client_id": client_id}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{self.base_url}/prompt", json=payload)
            if resp.status_code != 200:
                raise ComfyExecutionError(
                    f"ComfyUI rejected the workflow ({resp.status_code}): {resp.text}"
                )
            return resp.json()["prompt_id"]

    async def track_progress(
        self,
        prompt_id: str,
        client_id: str,
        on_progress: Callable[[int], None],
    ) -> None:
        """Listen on the WebSocket and report progress until the job completes.

        Best-effort: callers should still confirm the result via ``wait_for_history``.
        """
        uri = f"{self.ws_url}/ws?clientId={client_id}"
        async with websockets.connect(uri, max_size=None) as ws:
            async for message in ws:
                if isinstance(message, bytes):
                    # Binary frames are live preview images; ignore them.
                    continue
                data = json.loads(message)
                mtype = data.get("type")
                payload = data.get("data", {})
                if payload.get("prompt_id") not in (None, prompt_id):
                    continue
                if mtype == "progress":
                    value = payload.get("value", 0)
                    maximum = payload.get("max", 1) or 1
                    on_progress(int(value / maximum * 100))
                elif mtype == "executing" and payload.get("node") is None:
                    return  # Execution finished.
                elif mtype == "execution_error":
                    raise ComfyExecutionError(
                        payload.get("exception_message", "ComfyUI execution error")
                    )

    async def get_history(self, prompt_id: str) -> dict:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(f"{self.base_url}/history/{prompt_id}")
            resp.raise_for_status()
            return resp.json()

    async def wait_for_history(
        self, prompt_id: str, retries: int = 240, delay: float = 1.0
    ) -> dict:
        """Poll the history endpoint until outputs are available."""
        for _ in range(retries):
            history = await self.get_history(prompt_id)
            entry = history.get(prompt_id)
            if entry and entry.get("outputs"):
                return entry
            await asyncio.sleep(delay)
        raise ComfyExecutionError("Timed out waiting for ComfyUI to produce a result")

    async def fetch_image(
        self, filename: str, subfolder: str, folder_type: str
    ) -> bytes:
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(f"{self.base_url}/view", params=params)
            resp.raise_for_status()
            return resp.content

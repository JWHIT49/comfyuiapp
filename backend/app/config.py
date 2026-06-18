"""Application configuration loaded from environment variables / .env file."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base URL of the ComfyUI server (no trailing slash needed).
    comfyui_url: str = "http://127.0.0.1:8188"

    # Path to the API-format workflow template (relative to the backend folder).
    workflow_path: str = "workflows/flux_kontext_edit.json"

    # Where uploaded inputs and generated outputs are stored on disk.
    upload_dir: str = "uploads"
    output_dir: str = "outputs"

    # Comma-separated list of allowed CORS origins ("*" allows everything).
    cors_origins: str = "*"

    # Node IDs inside the workflow that the proxy rewrites per request.
    prompt_node_id: str = "7"   # CLIPTextEncode (the edit instruction)
    image_node_id: str = "4"    # LoadImage (the uploaded photo)
    sampler_node_id: str = "11"  # KSampler (seed)

    # How long to wait (seconds) for ComfyUI to finish a single job.
    result_timeout: float = 600.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

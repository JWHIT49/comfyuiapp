"""Load the workflow template and inject per-request values (prompt, image, seed)."""
from __future__ import annotations

import copy
import json
import random
from pathlib import Path

from .config import settings

_TEMPLATE: dict | None = None


def _load_template() -> dict:
    global _TEMPLATE
    if _TEMPLATE is None:
        path = Path(settings.workflow_path)
        with open(path, "r", encoding="utf-8") as fh:
            _TEMPLATE = json.load(fh)
    return _TEMPLATE


def build_workflow(prompt: str, image_name: str, seed: int | None = None) -> dict:
    """Return a fresh workflow dict with the user's prompt, image and a random seed."""
    workflow = copy.deepcopy(_load_template())
    workflow[settings.prompt_node_id]["inputs"]["text"] = prompt
    workflow[settings.image_node_id]["inputs"]["image"] = image_name
    if seed is None:
        seed = random.randint(0, 2**63 - 1)
    workflow[settings.sampler_node_id]["inputs"]["seed"] = seed
    return workflow

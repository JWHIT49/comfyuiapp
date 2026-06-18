# Backend — ComfyUI Image Edit Proxy

A small FastAPI service that sits between the mobile app and ComfyUI. It accepts
an image + a text instruction, runs the Flux Kontext editing workflow on ComfyUI,
and hands the finished image back to the app.

```
mobile app ──POST /jobs──▶ backend ──/upload/image, /prompt, /ws──▶ ComfyUI
                              │                                         │
        GET /jobs/{id} ◀──────┘   (polls progress, fetches result) ◀────┘
```

## Run it

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env      # edit COMFYUI_URL if needed
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`--host 0.0.0.0` is important: it lets your phone reach the backend over your
local network. Find your PC's LAN IP with `ipconfig` (look for IPv4 Address),
then point the app at `http://<that-ip>:8000`.

## API

| Method | Path                  | Body / Notes                                   |
|--------|-----------------------|------------------------------------------------|
| POST   | `/jobs`               | multipart form: `image` (file), `prompt` (text) → `{ job_id, status, ... }` |
| GET    | `/jobs/{job_id}`      | `{ status, progress, image_available, error }` |
| GET    | `/jobs/{job_id}/image`| the edited PNG once `status == completed`      |
| GET    | `/health`             | readiness probe                                |

### Quick test with curl

```powershell
curl.exe -F "prompt=Give him a hat" -F "image=@C:\path\to\photo.jpg" http://127.0.0.1:8000/jobs
# -> copy the job_id, then:
curl.exe http://127.0.0.1:8000/jobs/<job_id>
curl.exe http://127.0.0.1:8000/jobs/<job_id>/image --output result.png
```

## Notes

- Jobs are kept **in memory** and on disk under `outputs/`. Restarting the
  server clears the job list. That keeps the project dependency-free; swap in a
  database + a real queue (Redis/RQ, Celery) if you later need persistence or
  multiple workers.
- The workflow template lives in `workflows/flux_kontext_edit.json`. The node
  IDs the proxy rewrites (prompt / image / seed) are configured in
  `app/config.py`.

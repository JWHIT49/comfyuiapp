# ComfyUI Image Edit

Edit photos with plain-English instructions — *"Give him a hat," "Remove his
shoes," "Change the background to a beach"* — from an iPhone (or Android) app.
The heavy lifting runs on **ComfyUI** with the **Flux.1 Kontext [dev]** model,
which is purpose-built for instruction-based image editing.

> Built to be developed on **Windows without a Mac**: the app uses Expo, so you
> test on a real iPhone via Expo Go and build for the App Store with EAS Cloud.

## Architecture

```
┌────────────────┐   image + prompt   ┌───────────────────┐   workflow + image   ┌────────────┐
│  Mobile app    │ ─────────────────▶ │  Backend proxy    │ ───────────────────▶ │  ComfyUI   │
│  (Expo / RN)   │                    │  (FastAPI)        │                      │  Flux      │
│                │ ◀───────────────── │                   │ ◀─────────────────── │  Kontext   │
└────────────────┘   edited image     └───────────────────┘   finished image     └────────────┘
```

Three pieces, three folders:

| Folder      | What it is                          | Start here            |
|-------------|-------------------------------------|-----------------------|
| `comfyui/`  | Model download + ComfyUI run guide  | `comfyui/SETUP.md`    |
| `backend/`  | FastAPI proxy (jobs, progress, API) | `backend/README.md`   |
| `mobile/`   | Expo app (pick image, prompt, view) | `mobile/README.md`    |

## Quick start (end to end)

Do these in order. Each folder's README has the full detail.

1. **ComfyUI** — install it, download the Flux Kontext models, and start it
   listening on the network:
   ```powershell
   cd comfyui
   .\download_models.ps1 -ComfyPath "C:\ComfyUI_windows_portable\ComfyUI"
   # then start ComfyUI with: --listen 0.0.0.0 --port 8188
   ```

2. **Backend** — run the proxy that the app talks to:
   ```powershell
   cd backend
   python -m venv .venv; .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env       # set COMFYUI_URL if not localhost
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Mobile app** — point it at your PC's LAN IP and launch:
   ```powershell
   cd mobile
   npm install
   # edit app.json -> extra.apiBaseUrl = http://<your-PC-IP>:8000
   npm start                          # scan the QR code with Expo Go on your iPhone
   ```

## Requirements at a glance

- **GPU** for ComfyUI: ~12 GB VRAM ideal (8 GB works, slower). No GPU? Use a
  cloud GPU — see `comfyui/SETUP.md`.
- **Python 3.10+** for the backend.
- **Node.js 18+** + the **Expo Go** app for the mobile client.
- Same Wi-Fi network for phone ↔ PC.

## Swapping the editing model

Everything model-specific lives in `backend/workflows/flux_kontext_edit.json`
(an API-format ComfyUI graph) and the node IDs in `backend/app/config.py`. To
try a different editor (e.g. Qwen-Image-Edit, or a low-VRAM GGUF build of
Kontext), export that workflow from ComfyUI in API format, drop it in, and
update the three node IDs. No app or proxy code changes needed.

## Repo layout

```
.
├── comfyui/        # model download scripts + setup guide
├── backend/        # FastAPI proxy
│   ├── app/        #   main.py, comfy_client.py, workflow.py, jobs.py, ...
│   └── workflows/  #   flux_kontext_edit.json (API-format graph)
└── mobile/         # Expo app
    ├── App.js
    └── src/        #   api.js, config.js
```

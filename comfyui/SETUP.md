# ComfyUI Setup

The app's image editing runs entirely on **ComfyUI** using the **Flux.1 Kontext [dev]**
model, which is purpose-built for instruction edits like *"give him a hat"* or
*"remove his shoes."* You need one machine with an NVIDIA GPU to run it.

- **VRAM:** ~12 GB is comfortable with the `fp8` models used here. With 8 GB it
  still runs but slower (ComfyUI offloads to system RAM).
- **No local GPU?** Use a cloud GPU — see [Option B](#option-b-cloud-gpu).

---

## Option A — Windows (local NVIDIA GPU)

1. **Download ComfyUI (portable).** Get the latest
   `ComfyUI_windows_portable_nvidia.7z` from the
   [ComfyUI releases page](https://github.com/comfyanonymous/ComfyUI/releases)
   and extract it, e.g. to `C:\ComfyUI_windows_portable`.

2. **Download the models** with the helper script. From this folder:

   ```powershell
   .\download_models.ps1 -ComfyPath "C:\ComfyUI_windows_portable\ComfyUI"
   ```

   This places four files (~17 GB total):

   | File                                          | Folder                       |
   |-----------------------------------------------|------------------------------|
   | `flux1-dev-kontext_fp8_scaled.safetensors`    | `models\diffusion_models\`   |
   | `clip_l.safetensors`                          | `models\text_encoders\`      |
   | `t5xxl_fp8_e4m3fn_scaled.safetensors`         | `models\text_encoders\`      |
   | `ae.safetensors`                              | `models\vae\`                |

   > If a download returns 401, the repo needs a (free) Hugging Face login:
   > `pip install -U "huggingface_hub[cli]"` then `huggingface-cli login`, and
   > re-run the script.

3. **Start ComfyUI** so the backend (and your LAN) can reach it. Edit
   `run_nvidia_gpu.bat` or just launch with the listen flag:

   ```powershell
   cd C:\ComfyUI_windows_portable
   .\python_embeded\python.exe -s ComfyUI\main.py --listen 0.0.0.0 --port 8188
   ```

   Open <http://127.0.0.1:8188> — you should see the ComfyUI canvas.

4. **(Sanity check)** Drag `backend/workflows/flux_kontext_edit.json` onto the
   canvas. It is API-format, so it loads as a graph you can inspect. Pick an
   image in the `LoadImage` node, type an instruction in the `CLIPTextEncode`
   node, and press **Queue Prompt** to confirm everything works before wiring up
   the app.

---

## Option B — Cloud GPU

If you don't have a local GPU, rent one:

- **RunPod / Vast.ai:** start a "ComfyUI" community template (it comes with
  ComfyUI preinstalled), then run `download_models.sh` inside it:

  ```bash
  bash download_models.sh /workspace/ComfyUI
  ```

- Make sure ComfyUI is started with `--listen 0.0.0.0` and the pod exposes port
  `8188`. Point the backend's `COMFYUI_URL` at the pod's public address.

---

## How the workflow is driven

The backend never opens the UI. It uses ComfyUI's HTTP API:

1. `POST /upload/image` — sends the user's photo to ComfyUI's input folder.
2. `POST /prompt` — submits `backend/workflows/flux_kontext_edit.json` with the
   photo's filename and the user's instruction patched in.
3. WebSocket `/ws` — reports progress while the model runs.
4. `GET /view` — downloads the finished image.

You can swap the model later (e.g. Qwen-Image-Edit or a GGUF-quantized Kontext
for low VRAM) by replacing the workflow JSON and updating the node IDs in
`backend/app/config.py`.

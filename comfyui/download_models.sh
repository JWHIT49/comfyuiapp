#!/usr/bin/env bash
# Downloads the Flux.1 Kontext [dev] models into the correct ComfyUI folders.
# Usage: ./download_models.sh /path/to/ComfyUI
set -euo pipefail

COMFY="${1:-$HOME/ComfyUI}"
BASE="https://huggingface.co/Comfy-Org/flux1-kontext-dev_ComfyUI/resolve/main/split_files"

echo "ComfyUI path: $COMFY"
echo "This downloads ~17 GB."

download() {
  local url="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  if [[ -f "$dest" ]]; then
    echo "[skip] $dest"
  else
    echo "[get ] $url"
    curl -L --fail -o "$dest" "$url"
  fi
}

download "$BASE/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors" \
         "$COMFY/models/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors"
download "$BASE/text_encoders/clip_l.safetensors" \
         "$COMFY/models/text_encoders/clip_l.safetensors"
download "$BASE/text_encoders/t5xxl_fp8_e4m3fn_scaled.safetensors" \
         "$COMFY/models/text_encoders/t5xxl_fp8_e4m3fn_scaled.safetensors"
download "$BASE/vae/ae.safetensors" \
         "$COMFY/models/vae/ae.safetensors"

echo "Done. Models are in $COMFY/models"

<#
.SYNOPSIS
    Downloads the Flux.1 Kontext [dev] models that the editing workflow needs
    and places them in the correct ComfyUI model folders.

.EXAMPLE
    .\download_models.ps1 -ComfyPath "C:\ComfyUI_windows_portable\ComfyUI"
#>
param(
    [string]$ComfyPath = "$env:USERPROFILE\ComfyUI"
)

$ErrorActionPreference = "Stop"

$base = "https://huggingface.co/Comfy-Org/flux1-kontext-dev_ComfyUI/resolve/main/split_files"

$files = @(
    @{ Url = "$base/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors";
       Dest = "$ComfyPath\models\diffusion_models\flux1-dev-kontext_fp8_scaled.safetensors" },
    @{ Url = "$base/text_encoders/clip_l.safetensors";
       Dest = "$ComfyPath\models\text_encoders\clip_l.safetensors" },
    @{ Url = "$base/text_encoders/t5xxl_fp8_e4m3fn_scaled.safetensors";
       Dest = "$ComfyPath\models\text_encoders\t5xxl_fp8_e4m3fn_scaled.safetensors" },
    @{ Url = "$base/vae/ae.safetensors";
       Dest = "$ComfyPath\models\vae\ae.safetensors" }
)

Write-Host "ComfyUI path: $ComfyPath" -ForegroundColor Cyan
Write-Host "This downloads ~17 GB. Grab a coffee.`n" -ForegroundColor Yellow

foreach ($f in $files) {
    $dir = Split-Path $f.Dest -Parent
    New-Item -ItemType Directory -Force -Path $dir | Out-Null

    if (Test-Path $f.Dest) {
        Write-Host "[skip] already exists: $($f.Dest)" -ForegroundColor DarkGray
        continue
    }

    Write-Host "[get ] $($f.Url)" -ForegroundColor Green
    # curl.exe streams large files far better than Invoke-WebRequest.
    curl.exe -L --fail -o $f.Dest $f.Url
}

Write-Host "`nDone. Models are in $ComfyPath\models" -ForegroundColor Cyan

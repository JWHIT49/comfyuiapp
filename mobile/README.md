# Mobile App — ComfyUI Image Edit (Expo / React Native)

A cross-platform app (iOS + Android) that lets you pick a photo, type an
instruction like *"Give him a hat,"* and get the edited image back from the
ComfyUI backend. Built with **Expo** so you can develop and test on iPhone from
Windows — no Mac required.

## Prerequisites

- **Node.js 18+** on your PC.
- The **backend** running and reachable (see `../backend/README.md`).
- **ComfyUI** running with the Flux Kontext models (see `../comfyui/SETUP.md`).
- The **Expo Go** app installed on your iPhone (from the App Store), or an
  Android device/emulator.

## 1. Point the app at your backend

The app must reach your PC over the LAN. Find your PC's IPv4 address:

```powershell
ipconfig   # look for "IPv4 Address", e.g. 192.168.1.100
```

Open `app.json` and set `extra.apiBaseUrl` to `http://<that-ip>:8000`.
(Both phone and PC must be on the same Wi-Fi network.)

## 2. Install and run

```powershell
cd mobile
npm install
npm start
```

A QR code appears in the terminal. On your iPhone, open the **Camera** app and
scan it — it launches the project inside **Expo Go**. Pick a photo, type an
instruction, tap **Apply Edit**.

> First launch downloads JS to the phone, so give it a few seconds.

## 3. Building a real installable iOS app (later)

Expo Go is great for development. To ship a standalone `.ipa` for TestFlight /
the App Store **without a Mac**, use EAS Build (cloud):

```powershell
npm install -g eas-cli
eas login
eas build --platform ios
```

You'll need an Apple Developer account ($99/yr) for device installs and the
App Store. EAS handles the macOS build in the cloud.

## How it works

```
App.js  ──pick image + prompt──▶  src/api.js  ──HTTP──▶  backend (FastAPI)
   ▲                                   │
   └────── polls progress, shows ◀─────┘
           the returned image
```

- `src/config.js` — backend URL + prompt suggestions.
- `src/api.js` — `createJob`, `pollJob`, `jobImageUrl` (one function per endpoint).
- `App.js` — the single-screen UI (image picker, prompt box, progress, result).

## Notes / troubleshooting

- **"Network request failed":** the phone can't reach the backend. Confirm the
  IP in `app.json`, that the backend was started with `--host 0.0.0.0`, both
  devices share Wi-Fi, and your PC firewall allows inbound on port 8000.
- **Assets:** `app.json` references icon/splash images under `assets/`. Expo
  uses built-in placeholders if they're missing, so the app still runs. Drop
  your own PNGs in `mobile/assets/` to customize.

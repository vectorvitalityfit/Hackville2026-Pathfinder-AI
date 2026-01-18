# PathFinder AI — Voice Navigation Backend

This repository contains the backend for PathFinder AI — a voice-first assistive navigation service.

## What’s here
- `app/` — FastAPI application entrypoint and API handlers.
- `routes/` — Modular route handlers (brain, speech, vision).
- `start_server.ps1` — Windows helper to start Uvicorn.
- `requirements.txt` — Python dependencies.
- `api_keys.json` — (excluded from repo; do NOT commit keys — already in `.gitignore`).

## Project structure (current)

- app/
- routes/
- requirements.txt
- start_server.ps1
- README.md

## Quick setup

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
# run server
venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Notes
- `api_keys.json` is intentionally not tracked. Keep secrets out of the repo.
- This repo was reorganized to include minimal packaging metadata and a README.

## License
This project uses the Apache-2.0 license (see `LICENSE`).

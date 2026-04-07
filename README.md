# ProFace-Studio

AI-powered Telegram Bot + WebApp that transforms up to 5 personal photos into professional business headshots.

## Features

- Enforces exactly 5 photo uploads per generation.
- Fixed style templates (no free-text prompts):
  - LinkedIn-Style
  - Creative Studio
- Two-phase AI pipeline on Replicate:
  - Nano Banana 2: fast previews (2-3 options)
  - Nano Banana Pro: final high-quality render
- Telegram Stars checkout (`XTR`) before final generation.
- Neon PostgreSQL persistence for users, uploads, and transactions.
- Railway-ready (`Procfile` + `requirements.txt`).
- WebApp (`Flask`) for template selection, photo upload, and preview/final result rendering.

## Project Structure

- `main.py` - Telegram bot flow and handlers.
- `src/application/` - business services (generation orchestration).
- `src/domain/` - core entities.
- `src/infrastructure/` - database + AI adapters.
- `src/presentation/http/` - Flask routes.
- `src/presentation/telegram/` - Telegram integration entry points.
- `src/config/` - centralized settings loading.
- `database.py` - legacy compatibility wrapper source.
- `ai_pipeline.py` - legacy compatibility wrapper source.
- `web_app.py` - Flask WebApp server.
- `templates/index.html`, `static/*` - Web UI.
- `Procfile` - Railway worker command.
- `requirements.txt` - Python dependencies.
- `.env.example` - required environment variables.

## Environment Variables

Copy `.env.example` to `.env` and set:

- `TELEGRAM_TOKEN`
- `NEON_DATABASE_URL`
- `REPLICATE_API_TOKEN`
- `REPLICATE_PREVIEW_MODEL`
- `REPLICATE_FINAL_MODEL`
- `WEBAPP_URL` (optional, shown in bot `/start`)
- `PROFACE_PRICE_XTR` (default `49`)

## Run Locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Run WebApp:

```bash
python web_app.py
```

## WebApp Preview

![ProFace WebApp Home](docs/screenshots/webapp-home.png)

![ProFace WebApp Results](docs/screenshots/webapp-results.png)

## Reference Alignment

- Folder layout now mirrors the layered structure from the AZAMAT reference repository.
- WebApp visual style was adjusted toward the same top-bar/cards/hero look and feel.
- Generation flow remains adapted to ProFace requirements (fixed templates, 5 photo uploads, Stars-gated final render).

## Database Tables (Neon)

Initialized automatically on startup:

- `users` - user profile + current stage + selected template
- `uploads` - temporary 5 photo file IDs
- `transactions` - Telegram Stars invoices/payment states

## Telegram Stars Notes

- Currency is `XTR` using `sendInvoice`.
- Final rendering starts only after:
  - `pre_checkout_query` is approved
  - `successful_payment` is received

## API Alignment Notes

- Replicate integration now uploads Telegram image bytes via Replicate Files API instead of exposing Telegram file URLs.
- Generation calls try multiple common model input shapes (`input_images`, `images`, `image`) for better compatibility across model variants.
- Output normalization supports string URLs and Replicate file-like objects with `.url`.

## Validation

- Python syntax validation for bot/webapp modules (`py_compile`).
- End-to-end flow validated on code level:
  - template selection
  - exactly 5 uploads
  - paid-only final generation
  - preview-to-final handoff

## Railway Deployment (AZAMAT-style)

- `railway.toml` uses Nixpacks builder and project `nixpacks.toml`.
- Build pipeline installs Python + Node deps and runs `webapp-react` production build.
- Start command uses `web_app.py` to serve API + React mini app under `/webapp`.
- `Procfile` keeps optional split process definitions (`web` + `worker`) if you deploy worker separately.

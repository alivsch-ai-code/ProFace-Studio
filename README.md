# ProFace-Studio

AI-powered Telegram Bot that transforms up to 5 personal photos into professional business headshots.

## Features

- Enforces exactly 5 photo uploads per generation.
- Fixed style templates (no free-text prompts):
  - LinkedIn-Style
  - Creative Studio
- Two-phase AI pipeline:
  - Nano Banana 2: fast previews (2-3 options)
  - Nano Banana Pro: final high-quality render
- Telegram Stars checkout (`XTR`) before final generation.
- Neon PostgreSQL persistence for users, uploads, and transactions.
- Railway-ready (`Procfile` + `requirements.txt`).

## Project Structure

- `main.py` - Telegram bot flow and handlers.
- `database.py` - Neon/PostgreSQL connection and schema methods.
- `ai_pipeline.py` - Nano Banana API wrapper and prompt templates.
- `Procfile` - Railway worker command.
- `requirements.txt` - Python dependencies.
- `.env.example` - required environment variables.

## Environment Variables

Copy `.env.example` to `.env` and set:

- `TELEGRAM_TOKEN`
- `NEON_DATABASE_URL`
- `GEMINI_API_KEY`
- `GEMINI_BASE_URL` (optional adapter endpoint)
- `PROFACE_PRICE_XTR` (default `49`)

## Run Locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

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

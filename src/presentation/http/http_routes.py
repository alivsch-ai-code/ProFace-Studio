from __future__ import annotations

import os
import threading
import time
from typing import Any

from flask import Flask, jsonify, render_template, request, send_from_directory

from src.application.services import GenerationService
from src.infrastructure.ai.pipeline import SYSTEM_PROMPTS

MODEL_CATALOG = {
    "root": {
        "title": "ProFace Studio",
        "folders": [
            {"key": "styles", "title": "Styles", "path": "styles"},
        ],
        "models": [],
        "favorites_models": [
            {
                "key": "proface-nano-banana",
                "name": "ProFace Nano Banana",
                "description": "5-photo business portrait flow",
                "cost_credits": 49,
                "is_free": False,
                "menu_path": "styles",
            }
        ],
    },
    "styles": {
        "title": "Styles",
        "folders": [],
        "models": [
            {
                "key": "linkedin",
                "name": "LinkedIn Style",
                "description": "Clean, confident, business portrait.",
                "cost_credits": 49,
                "is_free": False,
                "menu_path": "styles",
            },
            {
                "key": "creative",
                "name": "Creative Studio",
                "description": "Cinematic and modern studio look.",
                "cost_credits": 49,
                "is_free": False,
                "menu_path": "styles",
            },
        ],
        "favorites_models": [],
    },
}

STRINGS_DE = {
    "webapp_user": "User",
    "webapp_settings": "Einstellungen",
    "webapp_credits_buy": "Credits kaufen",
    "menu_profile": "Profil",
    "webapp_free": "FREE",
    "webapp_title": "ProFace AI Hub",
    "webapp_choose_category": "Wähle eine Kategorie",
    "webapp_categories": "Kategorien",
    "webapp_back": "Zurück",
    "webapp_shop_title": "Credits kaufen",
    "webapp_credits_remaining": "Credits",
    "webapp_start": "Start",
}

ALLOWED_IMAGE_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 40 * 1024 * 1024
RATE_WINDOW_SEC = 10
RATE_MAX_ACTIONS_PER_IP = 30

_rate_lock = threading.Lock()
_rate_hits: dict[tuple[str, str], list[float]] = {}


def _client_ip() -> str:
    xff = (request.headers.get("X-Forwarded-For") or "").strip()
    if xff:
        return xff.split(",")[0].strip()
    return (request.remote_addr or "unknown").strip()


def _rate_limited(bucket: str, key: str, max_requests: int, window_seconds: int) -> bool:
    now = time.time()
    cutoff = now - max(1, int(window_seconds))
    k = (bucket, key)
    with _rate_lock:
        arr = _rate_hits.get(k, [])
        if arr:
            arr = [ts for ts in arr if ts >= cutoff]
        arr.append(now)
        _rate_hits[k] = arr
        return len(arr) > int(max_requests)


def register_flask_routes(app: Flask, generation_service: GenerationService, *, max_uploads: int = 5) -> None:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    react_dist = os.path.join(project_root, "webapp-react", "dist")

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            templates=list(SYSTEM_PROMPTS.keys()),
            max_uploads=max_uploads,
        )

    @app.post("/api/generate")
    def api_generate() -> Any:
        if _rate_limited("generate", _client_ip(), RATE_MAX_ACTIONS_PER_IP, RATE_WINDOW_SEC):
            return jsonify({"ok": False, "error": "rate_limited"}), 429

        style = request.form.get("style", "linkedin")
        if style not in SYSTEM_PROMPTS:
            return jsonify({"ok": False, "error": "invalid_style"}), 400

        req_files = request.files.getlist("photos")
        if len(req_files) != max_uploads:
            return jsonify({"ok": False, "error": "need_exactly_5_photos"}), 400

        files: list[tuple[bytes, str]] = []
        total_bytes = 0
        for f in req_files:
            content = f.read()
            if not content:
                return jsonify({"ok": False, "error": "empty_file"}), 400
            mime = f.mimetype or "image/jpeg"
            if mime not in ALLOWED_IMAGE_MIME:
                return jsonify({"ok": False, "error": "unsupported_mime_type"}), 400
            if len(content) > MAX_FILE_BYTES:
                return jsonify({"ok": False, "error": "file_too_large"}), 413
            total_bytes += len(content)
            if total_bytes > MAX_TOTAL_BYTES:
                return jsonify({"ok": False, "error": "payload_too_large"}), 413
            files.append((content, mime))

        return jsonify(generation_service.generate_from_uploads(style, files))

    @app.get("/webapp")
    def webapp_index():
        if os.path.isdir(react_dist):
            return send_from_directory(react_dist, "index.html")
        return render_template("index.html", templates=list(SYSTEM_PROMPTS.keys()), max_uploads=max_uploads)

    @app.get("/webapp/<path:path>")
    def webapp_assets(path: str):
        if os.path.isdir(react_dist):
            return send_from_directory(react_dist, path)
        return ("Not built", 404)

    @app.get("/api/user")
    def api_user() -> Any:
        return jsonify(
            {
                "user_id": 1,
                "username": "proface_user",
                "credits": 0,
                "lang": "de",
                "auto_opt": True,
                "daily_msg": False,
                "bot_username": "proface_bot",
            }
        )

    @app.post("/api/user_info")
    def api_user_info() -> Any:
        # Telegram init_data verification can be added here for production hardening.
        base = {
            "ok": True,
            "user_id": 1,
            "username": "proface_user",
            "credits": 0,
            "lang": "de",
            "auto_opt": True,
            "daily_msg": False,
            "bot_username": "proface_bot",
        }
        return jsonify(base)

    @app.get("/api/version")
    def api_version() -> Any:
        return jsonify({"version": "0.1.0"})

    @app.get("/api/strings")
    def api_strings() -> Any:
        _lang = request.args.get("lang", "de")
        return jsonify(STRINGS_DE)

    @app.get("/api/legal")
    def api_legal() -> Any:
        _lang = request.args.get("lang", "de")
        return jsonify(
            {
                "ok": True,
                "privacy": "Datenschutz: ProFace verarbeitet Uploads zur Bildgenerierung.",
                "impressum": "Impressum: ProFace Studio.",
                "labels": {
                    "doc_privacy_title": "Datenschutz",
                    "doc_impressum_title": "Impressum",
                    "back": "Zurück",
                },
            }
        )

    @app.get("/api/models")
    def api_models() -> Any:
        path = request.args.get("path", "root")
        data = MODEL_CATALOG.get(path, MODEL_CATALOG["root"])
        return jsonify(data)

    @app.get("/api/model_detail")
    def api_model_detail() -> Any:
        key = request.args.get("key", "linkedin")
        if key not in SYSTEM_PROMPTS:
            return jsonify({"ok": False, "error": "model_not_found"}), 404
        return jsonify(
            {
                "ok": True,
                "key": key,
                "name": "LinkedIn Style" if key == "linkedin" else "Creative Studio",
                "description": SYSTEM_PROMPTS[key],
                "cost_credits": 49,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "photos": {"type": "array", "minItems": 5, "maxItems": 5},
                    },
                    "required": ["photos"],
                },
            }
        )

    @app.get("/api/shop_packages")
    def api_shop_packages() -> Any:
        return jsonify(
            {
                "ok": True,
                "packages": [
                    {"credits": 50, "price_xtr": 49},
                    {"credits": 120, "price_xtr": 99},
                    {"credits": 260, "price_xtr": 199},
                ],
            }
        )

    @app.post("/api/action")
    def api_action() -> Any:
        if _rate_limited("action", _client_ip(), RATE_MAX_ACTIONS_PER_IP, RATE_WINDOW_SEC):
            return jsonify({"ok": False, "error": "rate_limited"}), 429
        data = request.get_json(silent=True) or {}
        action = str(data.get("action") or "")
        return jsonify({"ok": True, "action": action})

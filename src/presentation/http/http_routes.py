from __future__ import annotations

import os
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
}


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
        style = request.form.get("style", "linkedin")
        if style not in SYSTEM_PROMPTS:
            return jsonify({"ok": False, "error": "invalid_style"}), 400

        req_files = request.files.getlist("photos")
        if len(req_files) != max_uploads:
            return jsonify({"ok": False, "error": "need_exactly_5_photos"}), 400

        files: list[tuple[bytes, str]] = []
        for f in req_files:
            content = f.read()
            if not content:
                return jsonify({"ok": False, "error": "empty_file"}), 400
            mime = f.mimetype or "image/jpeg"
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

    @app.get("/api/version")
    def api_version() -> Any:
        return jsonify({"version": "0.1.0"})

    @app.get("/api/strings")
    def api_strings() -> Any:
        _lang = request.args.get("lang", "de")
        return jsonify(STRINGS_DE)

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
        data = request.get_json(silent=True) or {}
        action = str(data.get("action") or "")
        return jsonify({"ok": True, "action": action})

import base64
import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from ai_pipeline import AIPipeline, SYSTEM_PROMPTS


load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
REPLICATE_PREVIEW_MODEL = os.getenv("REPLICATE_PREVIEW_MODEL", "google/nano-banana-2")
REPLICATE_FINAL_MODEL = os.getenv("REPLICATE_FINAL_MODEL", "google/nano-banana-pro")
MAX_UPLOADS = 5

ai = AIPipeline(
    api_key=REPLICATE_API_TOKEN,
    preview_model=REPLICATE_PREVIEW_MODEL,
    final_model=REPLICATE_FINAL_MODEL,
)

app = Flask(__name__)


def _to_data_url(content: bytes, mime: str) -> str:
    encoded = base64.b64encode(content).decode("ascii")
    return f"data:{mime};base64,{encoded}"


@app.get("/")
def index():
    return render_template("index.html", templates=list(SYSTEM_PROMPTS.keys()), max_uploads=MAX_UPLOADS)


@app.post("/api/generate")
def generate() -> Any:
    style = request.form.get("style", "linkedin")
    if style not in SYSTEM_PROMPTS:
        return jsonify({"ok": False, "error": "invalid_style"}), 400

    files = request.files.getlist("photos")
    if len(files) != MAX_UPLOADS:
        return jsonify({"ok": False, "error": "need_exactly_5_photos"}), 400

    data_urls: list[str] = []
    for f in files:
        content = f.read()
        if not content:
            return jsonify({"ok": False, "error": "empty_file"}), 400
        mime = f.mimetype or "image/jpeg"
        data_urls.append(_to_data_url(content, mime))

    previews = ai.generate_previews(style, data_urls)
    final_url = ai.generate_final(style, data_urls, previews[0] if previews else None)
    return jsonify(
        {
            "ok": True,
            "style": style,
            "previews": previews,
            "final_url": final_url,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")), debug=False)

from flask import Flask

from src.presentation.http.http_routes import register_flask_routes


class _FakeGenerationService:
    def generate_from_uploads(self, style, files):
        return {"ok": True, "style": style, "previews": ["https://x/a.png"], "final_url": "https://x/f.png"}


def _app():
    app = Flask(__name__, template_folder="../templates")
    register_flask_routes(app, _FakeGenerationService(), max_uploads=5)
    return app


def test_models_endpoint():
    client = _app().test_client()
    res = client.get("/api/models?path=styles")
    assert res.status_code == 200
    body = res.get_json()
    assert "models" in body
    assert len(body["models"]) >= 1


def test_model_detail_not_found():
    client = _app().test_client()
    res = client.get("/api/model_detail?key=unknown")
    assert res.status_code == 404


def test_generate_needs_exactly_five_uploads():
    client = _app().test_client()
    res = client.post("/api/generate", data={"style": "linkedin"})
    assert res.status_code == 400
    assert res.get_json()["error"] == "need_exactly_5_photos"

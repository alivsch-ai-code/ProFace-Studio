from io import BytesIO

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


def test_webapp_route_available():
    client = _app().test_client()
    res = client.get("/webapp")
    assert res.status_code == 200


def test_generate_success_with_exactly_five_uploads():
    client = _app().test_client()
    data = {
        "style": "linkedin",
        "photos": [
            (BytesIO(b"img-1"), "1.jpg"),
            (BytesIO(b"img-2"), "2.jpg"),
            (BytesIO(b"img-3"), "3.jpg"),
            (BytesIO(b"img-4"), "4.jpg"),
            (BytesIO(b"img-5"), "5.jpg"),
        ],
    }
    res = client.post("/api/generate", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["style"] == "linkedin"
    assert body["final_url"].startswith("https://")


def test_generate_rejects_invalid_style():
    client = _app().test_client()
    data = {
        "style": "invalid-style",
        "photos": [
            (BytesIO(b"img-1"), "1.jpg"),
            (BytesIO(b"img-2"), "2.jpg"),
            (BytesIO(b"img-3"), "3.jpg"),
            (BytesIO(b"img-4"), "4.jpg"),
            (BytesIO(b"img-5"), "5.jpg"),
        ],
    }
    res = client.post("/api/generate", data=data, content_type="multipart/form-data")
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_style"


def test_api_contract_endpoints_basic_shape():
    client = _app().test_client()

    user = client.get("/api/user")
    assert user.status_code == 200
    user_body = user.get_json()
    assert "username" in user_body and "credits" in user_body

    version = client.get("/api/version")
    assert version.status_code == 200
    assert "version" in version.get_json()

    shop = client.get("/api/shop_packages")
    assert shop.status_code == 200
    shop_body = shop.get_json()
    assert shop_body["ok"] is True
    assert isinstance(shop_body["packages"], list)


def test_generate_rejects_unsupported_mime_type():
    client = _app().test_client()
    data = {
        "style": "linkedin",
        "photos": [
            (BytesIO(b"x"), "1.gif"),
            (BytesIO(b"x"), "2.gif"),
            (BytesIO(b"x"), "3.gif"),
            (BytesIO(b"x"), "4.gif"),
            (BytesIO(b"x"), "5.gif"),
        ],
    }
    res = client.post("/api/generate", data=data, content_type="multipart/form-data")
    assert res.status_code == 400
    assert res.get_json()["error"] == "unsupported_mime_type"


def test_generate_rejects_too_large_payload():
    client = _app().test_client()
    huge = b"a" * (8 * 1024 * 1024 + 1)
    data = {
        "style": "linkedin",
        "photos": [
            (BytesIO(huge), "1.jpg"),
            (BytesIO(b"x"), "2.jpg"),
            (BytesIO(b"x"), "3.jpg"),
            (BytesIO(b"x"), "4.jpg"),
            (BytesIO(b"x"), "5.jpg"),
        ],
    }
    res = client.post("/api/generate", data=data, content_type="multipart/form-data")
    assert res.status_code == 413
    assert res.get_json()["error"] == "file_too_large"

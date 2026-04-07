import os

from dotenv import load_dotenv
from flask import Flask

from src.application.services import GenerationService
from src.config.settings import load_settings
from src.infrastructure.ai.pipeline import AIPipeline
from src.presentation.http.http_routes import register_flask_routes


load_dotenv()
settings = load_settings()
MAX_UPLOADS = 5

ai = AIPipeline(
    api_key=settings.replicate_api_token,
    preview_model=settings.replicate_preview_model,
    final_model=settings.replicate_final_model,
)
generation_service = GenerationService(ai)

app = Flask(__name__)
register_flask_routes(app, generation_service, max_uploads=MAX_UPLOADS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.port, debug=False)

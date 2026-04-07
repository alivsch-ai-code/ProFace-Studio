import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    neon_database_url: str
    replicate_api_token: str
    replicate_preview_model: str
    replicate_final_model: str
    webapp_url: str
    proface_price_xtr: int
    port: int


def load_settings() -> Settings:
    return Settings(
        telegram_token=os.getenv("TELEGRAM_TOKEN", "").strip(),
        neon_database_url=os.getenv("NEON_DATABASE_URL", "").strip(),
        replicate_api_token=os.getenv("REPLICATE_API_TOKEN", "").strip(),
        replicate_preview_model=os.getenv("REPLICATE_PREVIEW_MODEL", "google/nano-banana-2").strip(),
        replicate_final_model=os.getenv("REPLICATE_FINAL_MODEL", "google/nano-banana-pro").strip(),
        webapp_url=os.getenv("WEBAPP_URL", "").strip(),
        proface_price_xtr=int(os.getenv("PROFACE_PRICE_XTR", "49")),
        port=int(os.getenv("PORT", "8080")),
    )

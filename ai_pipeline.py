import hashlib
import os
from typing import Iterable

import requests


SYSTEM_PROMPTS = {
    "linkedin": "Professional business portrait, studio lighting, high resolution, wearing a suit, clean background, confident look.",
    "creative": "Creative studio portrait, professional quality, cinematic light, modern business style, polished composition.",
}


class AIPipeline:
    """
    2-Phasen Pipeline:
    - Phase 1: schnelle Vorschauen (Nano Banana 2)
    - Phase 2: finales HQ-Rendering (Nano Banana Pro)

    Falls kein API-Endpoint konfiguriert ist, liefert die Klasse deterministische
    Placeholder-URLs zurück, damit der Bot-Flow testbar bleibt.
    """

    def __init__(self, api_key: str, base_url: str | None = None):
        self.api_key = api_key
        self.base_url = (base_url or "").strip().rstrip("/")

    def _placeholder_urls(self, seed_prefix: str, count: int) -> list[str]:
        out = []
        for i in range(count):
            seed = hashlib.sha1(f"{seed_prefix}:{i}".encode()).hexdigest()[:16]
            out.append(f"https://picsum.photos/seed/{seed}/1024/1024")
        return out

    def generate_previews(self, style_key: str, file_ids: Iterable[str]) -> list[str]:
        file_ids = list(file_ids)
        prompt = SYSTEM_PROMPTS.get(style_key, SYSTEM_PROMPTS["linkedin"])
        if not self.base_url:
            return self._placeholder_urls(f"preview:{style_key}:{','.join(file_ids)}", 3)

        resp = requests.post(
            f"{self.base_url}/nano-banana-2/previews",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"prompt": prompt, "file_ids": file_ids, "count": 3},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json() or {}
        urls = data.get("urls") or []
        return [u for u in urls if isinstance(u, str)]

    def generate_final(self, style_key: str, file_ids: Iterable[str], chosen_preview_url: str | None) -> str:
        file_ids = list(file_ids)
        prompt = SYSTEM_PROMPTS.get(style_key, SYSTEM_PROMPTS["linkedin"])
        if not self.base_url:
            return self._placeholder_urls(
                f"final:{style_key}:{chosen_preview_url}:{','.join(file_ids)}", 1
            )[0]

        resp = requests.post(
            f"{self.base_url}/nano-banana-pro/final",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "prompt": prompt,
                "file_ids": file_ids,
                "chosen_preview_url": chosen_preview_url,
            },
            timeout=240,
        )
        resp.raise_for_status()
        data = resp.json() or {}
        url = data.get("url")
        if not isinstance(url, str) or not url:
            raise RuntimeError("Nano Banana Pro returned no final url")
        return url

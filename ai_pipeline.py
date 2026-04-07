import hashlib
import io
from typing import Any, Iterable

SYSTEM_PROMPTS = {
    "linkedin": "Professional business portrait, studio lighting, high resolution, wearing a suit, clean background, confident look.",
    "creative": "Creative studio portrait, professional quality, cinematic light, modern business style, polished composition.",
}


class AIPipeline:
    """Replicate-basierte 2-Phasen Pipeline für ProFace."""

    def __init__(self, api_key: str, preview_model: str, final_model: str):
        self._import_error: str | None = None
        try:
            import replicate  # type: ignore

            self.client = replicate.Client(api_token=api_key)
        except Exception as exc:
            self.client = None
            self._import_error = str(exc)
        self.preview_model = preview_model
        self.final_model = final_model

    def _placeholder_urls(self, seed_prefix: str, count: int) -> list[str]:
        out = []
        for i in range(count):
            seed = hashlib.sha1(f"{seed_prefix}:{i}".encode()).hexdigest()[:16]
            out.append(f"https://picsum.photos/seed/{seed}/1024/1024")
        return out

    @staticmethod
    def _normalize_output_urls(output: Any) -> list[str]:
        urls: list[str] = []
        if isinstance(output, str):
            return [output]
        if isinstance(output, list):
            for item in output:
                if isinstance(item, str):
                    urls.append(item)
                elif hasattr(item, "url"):
                    try:
                        val = item.url() if callable(item.url) else item.url
                        if val:
                            urls.append(str(val))
                    except Exception:
                        continue
            return urls
        if hasattr(output, "url"):
            try:
                val = output.url() if callable(output.url) else output.url
                return [str(val)] if val else []
            except Exception:
                return []
        return urls

    def upload_image_bytes(self, content: bytes, filename: str = "upload.jpg") -> str | None:
        if self.client is None:
            return None
        try:
            file_obj = self.client.files.create(io.BytesIO(content), filename=filename)
            val = file_obj.url() if hasattr(file_obj, "url") and callable(file_obj.url) else getattr(file_obj, "url", None)
            return str(val) if val else None
        except Exception:
            return None

    def generate_previews(self, style_key: str, image_inputs: Iterable[str]) -> list[str]:
        image_inputs = list(image_inputs)
        prompt = SYSTEM_PROMPTS.get(style_key, SYSTEM_PROMPTS["linkedin"])
        if not image_inputs:
            return []
        if self.client is None:
            return self._placeholder_urls(f"preview:{style_key}:{','.join(image_inputs)}", 3)
        try:
            input_payloads = [
                {"prompt": prompt, "input_images": image_inputs[:5], "num_outputs": 3},
                {"prompt": prompt, "images": image_inputs[:5], "num_outputs": 3},
                {"prompt": prompt, "image": image_inputs[0], "num_outputs": 3},
            ]
            output = None
            for payload in input_payloads:
                try:
                    output = self.client.run(self.preview_model, input=payload)
                    break
                except Exception:
                    output = None
                    continue
            if output is None:
                raise RuntimeError("preview_generation_failed")
            urls = self._normalize_output_urls(output)
            return urls[:3]
        except Exception:
            return self._placeholder_urls(f"preview:{style_key}:{','.join(image_inputs)}", 3)

    def generate_final(
        self,
        style_key: str,
        image_inputs: Iterable[str],
        chosen_preview_url: str | None,
    ) -> str:
        image_inputs = list(image_inputs)
        prompt = SYSTEM_PROMPTS.get(style_key, SYSTEM_PROMPTS["linkedin"])
        if self.client is None:
            return self._placeholder_urls(
                f"final:{style_key}:{chosen_preview_url}:{','.join(image_inputs)}", 1
            )[0]
        try:
            input_payloads = [
                {
                    "prompt": prompt,
                    "input_images": image_inputs[:5],
                    "reference_image": chosen_preview_url,
                    "num_outputs": 1,
                },
                {
                    "prompt": prompt,
                    "images": image_inputs[:5],
                    "image": chosen_preview_url or image_inputs[0],
                    "num_outputs": 1,
                },
                {"prompt": prompt, "image": image_inputs[0], "num_outputs": 1},
            ]
            output = None
            for payload in input_payloads:
                try:
                    output = self.client.run(self.final_model, input=payload)
                    break
                except Exception:
                    output = None
                    continue
            if output is None:
                raise RuntimeError("final_generation_failed")
            urls = self._normalize_output_urls(output)
            if urls:
                return urls[0]
        except Exception:
            pass
        return self._placeholder_urls(
            f"final:{style_key}:{chosen_preview_url}:{','.join(image_inputs)}", 1
        )[0]

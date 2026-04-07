import base64

from src.infrastructure.ai.pipeline import AIPipeline


class GenerationService:
    def __init__(self, pipeline: AIPipeline):
        self.pipeline = pipeline

    @staticmethod
    def to_data_url(content: bytes, mime: str) -> str:
        encoded = base64.b64encode(content).decode("ascii")
        return f"data:{mime};base64,{encoded}"

    def generate_from_uploads(self, style: str, files: list[tuple[bytes, str]]) -> dict:
        inputs = [self.to_data_url(content, mime) for content, mime in files]
        previews = self.pipeline.generate_previews(style, inputs)
        final_url = self.pipeline.generate_final(style, inputs, previews[0] if previews else None)
        return {"ok": True, "style": style, "previews": previews, "final_url": final_url}

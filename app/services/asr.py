from __future__ import annotations
from dataclasses import dataclass
from ..config import settings

try:
    from faster_whisper import WhisperModel
except Exception as e:  # покажем, что именно не хватает
    print("FASTWHISPER_IMPORT_ERROR:", repr(e))
    WhisperModel = None  # type: ignore


@dataclass
class ASRResult:
    text: str

class ASREngine:
    def __init__(self) -> None:
        self.stub = settings.app.stub_asr
        self.language = settings.whisper.language
        self.model = None
        if not self.stub:
            assert WhisperModel is not None, "faster-whisper is not installed"
            self.model = WhisperModel(
                settings.whisper.model,
                device=settings.whisper.device,
                compute_type=settings.whisper.compute_type,
            )

    def transcribe_file(self, path: str) -> ASRResult:
        if self.stub:
            text = (
                "Здравствуйте. Это тестовая запись. Мы проверяем модуль распознавания. "
                "Пожалуйста, разделите текст на предложения. Спасибо."
            )
            return ASRResult(text=text)
        assert self.model is not None
        segments, info = self.model.transcribe(
            path,
            language=self.language,
            vad_filter=settings.whisper.vad_filter,
            temperature=settings.whisper.temperature,
            condition_on_previous_text=True,
        )
        text_parts = []
        for seg in segments:
            text_parts.append(seg.text)
        text = " ".join(text_parts).strip()
        return ASRResult(text=text)
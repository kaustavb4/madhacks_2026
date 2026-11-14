"""Speech-to-text: Deepgram if DEEPGRAM_API_KEY is set, else a mock."""
import os


class STT:
    def transcribe(self, audio_bytes: bytes) -> str:
        raise NotImplementedError


class DeepgramSTT(STT):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def transcribe(self, audio_bytes: bytes) -> str:
        import requests

        resp = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers={
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/wav",
            },
            data=audio_bytes,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["results"]["channels"][0]["alternatives"][0]["transcript"]


class MockSTT(STT):
    """Returns a canned phrase so the rest of the pipeline can be exercised
    without a real STT key. Swap in real audio-based mocking as needed."""

    def transcribe(self, audio_bytes: bytes) -> str:
        return "make a keyring tag fifty by twenty by three millimeters"


def get_stt() -> STT:
    key = os.getenv("DEEPGRAM_API_KEY")
    return DeepgramSTT(key) if key else MockSTT()

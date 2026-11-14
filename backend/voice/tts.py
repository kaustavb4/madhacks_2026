"""Text-to-speech: ElevenLabs if ELEVENLABS_API_KEY is set, else a mock."""
import os


class TTS:
    def speak(self, text: str) -> bytes:
        """Return audio bytes (mp3) for the given text."""
        raise NotImplementedError


class ElevenLabsTTS(TTS):
    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        self.api_key = api_key
        self.voice_id = voice_id

    def speak(self, text: str) -> bytes:
        import requests

        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}",
            headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
            json={"text": text, "model_id": "eleven_monolingual_v1"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.content


class MockTTS(TTS):
    """Returns empty audio; the text itself is what matters for dev/testing."""

    def speak(self, text: str) -> bytes:
        return b""


def get_tts() -> TTS:
    key = os.getenv("ELEVENLABS_API_KEY")
    return ElevenLabsTTS(key) if key else MockTTS()

"""Voice in -> LLM tool-calling agent -> CAD/measure/slicer tools -> voice out.

One global Session for the hackathon demo (single maker, single conversation).
"""
import json

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from backend.llm.agent import get_agent
from backend.llm.dispatch import execute_tool
from backend.session import Session
from backend.voice.stt import get_stt
from backend.voice.tts import get_tts

app = FastAPI(title="Voice CAD to Print")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

stt = get_stt()
tts = get_tts()
agent = get_agent()
session = Session()
conversation: list[dict] = []

MAX_TOOL_STEPS = 6  # safety cap so a tool-call loop can't run forever


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/stt")
async def speech_to_text(audio: UploadFile):
    audio_bytes = await audio.read()
    text = stt.transcribe(audio_bytes)
    return {"text": text}


@app.post("/tts")
def text_to_speech(text: str):
    audio_bytes = tts.speak(text)
    return Response(content=audio_bytes, media_type="audio/mpeg")


def run_agent_turn(user_text: str) -> str:
    """Appends the user's message, runs the tool-calling loop until the
    agent gives a final spoken reply, and returns that reply text."""
    conversation.append({"role": "user", "content": user_text})

    for _ in range(MAX_TOOL_STEPS):
        message = agent.step(conversation)
        conversation.append(message)

        tool_calls = message.get("tool_calls")
        if not tool_calls:
            return message.get("content") or ""

        for call in tool_calls:
            args = json.loads(call["function"]["arguments"])
            try:
                result = execute_tool(call["function"]["name"], args, session)
            except Exception as exc:  # surfaced to the LLM to retry/explain, per design doc
                result = {"error": str(exc)}
            conversation.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": json.dumps(result),
            })

    return "Sorry, that took too many steps -- can you repeat what you need?"


@app.post("/converse")
async def converse(audio: UploadFile):
    """Hold-to-talk round trip: audio in, spoken reply out."""
    audio_bytes = await audio.read()
    heard = stt.transcribe(audio_bytes)
    reply_text = run_agent_turn(heard)
    reply_audio = tts.speak(reply_text)
    return Response(
        content=reply_audio,
        media_type="audio/mpeg",
        headers={"X-Heard": heard, "X-Reply": reply_text},
    )

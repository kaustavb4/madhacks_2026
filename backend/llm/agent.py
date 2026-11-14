"""Tool-calling agent loop. Uses Groq (OpenAI-compatible chat completions,
model llama-3.3-70b-versatile) if GROQ_KEY is set, else a scripted mock so
the pipeline runs end to end without a key.
"""
import json
import os

from backend.llm.tools import TOOLS

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are Jarvis, a voice assistant that helps a blind maker design and "
    "print a part. You only act through the given tools: ask_intent, "
    "create_model, edit_model, measure, check_printable, set_print_settings, "
    "print, pause, cancel, undo. Never state a measurement yourself -- always "
    "call measure() and read back its result. Confirm every number with the "
    "user before moving on."
)


def _to_openai_tools(tools: list[dict]) -> list[dict]:
    return [{"type": "function", "function": t} for t in tools]


class Agent:
    def step(self, messages: list[dict]) -> dict:
        """Given conversation history, return the next assistant message
        (possibly with tool_calls) as a plain dict."""
        raise NotImplementedError


class GroqAgent(Agent):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def step(self, messages: list[dict]) -> dict:
        import requests

        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]
        resp = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": GROQ_MODEL,
                "messages": full_messages,
                "tools": _to_openai_tools(TOOLS),
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]


class MockAgent(Agent):
    """Deterministic one-shot script: always create a default plate with a
    hole, so Parts 2-4 can be exercised without a real LLM key."""

    def step(self, messages: list[dict]) -> dict:
        if not any(m.get("role") == "tool" for m in messages):
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "mock-1",
                    "type": "function",
                    "function": {
                        "name": "create_model",
                        "arguments": json.dumps({
                            "template": "plate_with_hole",
                            "params": {"length": 50, "width": 20, "thickness": 3,
                                       "hole_diameter": 4, "hole_offset_x": 6},
                        }),
                    },
                }],
            }
        return {"role": "assistant", "content": "Your tag is 50 by 20 by 3 millimeters. OK?"}


def get_agent() -> Agent:
    key = os.getenv("GROQ_KEY")
    return GroqAgent(key) if key else MockAgent()

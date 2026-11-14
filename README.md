# Voice CAD to Print

Voice assistant that takes a blind maker from a spoken idea to a printed part:
voice in/out, LLM-driven CadQuery modeling, measured readback, voice-controlled
slicing and printing. See `docs/PLAN.md` for the build plan and repo layout.

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys as you get them; blank = mock mode
```

## Run the voice loop (Part 1)
```bash
uvicorn backend.main:app --reload
```
Then open `frontend/index.html` in a browser. Hold spacebar to talk.

Every external service (speech-to-text, text-to-speech, the LLM, the slicer,
the printer) runs in mock mode until its env var / binary is present — see
`docs/PLAN.md` → Mock strategy.

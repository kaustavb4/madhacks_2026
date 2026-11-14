# AGENTS.md — Voice CAD to Print

Context for any AI coding agent (Claude Code, Cursor, etc.) working in this repo.

## What this is
Voice assistant that takes a blind maker from a spoken idea to a printed part:
voice in/out → LLM-driven CadQuery modeling → measured readback → voice-controlled
slicing and printing. No screen, no code, for the user. Full product spec lives in
`docs/PLAN.md`; read that first for the "why" behind every design choice below.

## Current state (check before building — don't re-scaffold what exists)
- **Part 1 (voice loop)**: done. `backend/voice/{stt,tts}.py`, `frontend/{index.html,app.js}`.
- **Part 2 (CAD + LLM agent)**: done. `backend/cad/{model,templates,braille}.py`,
  `backend/llm/{agent,tools,dispatch,design_log}.py`.
- **Part 3 (measuring + checks)**: done. `backend/measure/{measure,checks}.py`.
- **Part 4 (slicing + printing)**: stubbed, mock-only (no real printer key yet).
  `backend/slicer/{slice,printer}.py`.
- `backend/main.py` wires the full loop: audio in → STT → agent tool loop → TTS → audio out.
- `backend/session.py` holds the one global in-memory session (model, design log, printer).

## Hard rules — don't violate these
1. **The LLM never writes CadQuery code or states a measurement.** It only calls the
   fixed tools in `backend/llm/tools.py` (`create_model`, `edit_model`, `measure`, ...).
   Real numbers come only from `backend/measure/measure.py` querying the actual solid/mesh.
2. **Every CAD build goes through named-parameter templates** in `backend/cad/templates.py`,
   never raw ad-hoc CadQuery in the agent layer. New part types = new template function,
   registered in `TEMPLATES`.
3. **Every external integration (STT, TTS, LLM, slicer, printer) has a mock fallback**,
   selected by whether its env var / binary is present (see each `get_*()` factory
   function). Never make a new integration hard-require a key — the pipeline must run
   end to end with zero keys set.
4. **Secrets live only in `.env`** (gitignored). `.env.example` documents key *names*
   only, never real values. Current keys: `DEEPGRAM_API_KEY`, `GROQ_KEY` (LLM — Groq,
   OpenAI-compatible chat completions, NOT Anthropic), `ELEVENLABS_API_KEY`,
   `PRINTER_URL`, `PRINTER_API_KEY`.
5. **Model edits are undo-able.** `backend/cad/model.py`'s `Model` class keeps a full
   history; `undo()` must keep working after any change to `edit()`/`create()`.

## Setup
```bash
# cadquery needs Python 3.11 (no OCP wheel for 3.12+/3.13+/3.15 yet as of this writing)
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys as you get them; blank = mock mode
```

## Run / test
```bash
uvicorn backend.main:app --reload     # backend, then open frontend/index.html
python3 -m pytest tests/ -q           # 5 tests, should all pass with zero env keys set
```

## Who owns what (original team spec, see docs/PLAN.md for detail)
- Person 1: voice loop (`backend/voice/`, `frontend/`)
- Person 2: LLM + CadQuery (`backend/llm/`, `backend/cad/`)
- Person 3: measuring + checks (`backend/measure/`)
- Person 4: slicing + printing (`backend/slicer/`)

## Known gaps / next steps
- Real Groq key not yet tested end to end (mock agent verified the plumbing).
- `PRINTER_API_KEY` pending — get it from the printer's own OctoPrint/PrusaLink
  settings once hardware is available; it's free, not purchased.
- `backend/measure/measure.py:min_wall_thickness` is a naive per-face ray cast
  (marked `ponytail:` in the code) — fine for flat/boxy parts, may misread
  thin curved walls.

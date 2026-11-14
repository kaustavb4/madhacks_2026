# Voice CAD to Print — Plan

## Scope (solo build, MadHacks 2026)
Scaffold all 4 roles, mock every external API behind `.env` flags, implement Part 1 (voice loop) first.

## Repo layout
```
backend/
  main.py          FastAPI app, wires voice <-> llm agent
  voice/
    stt.py         speech-to-text: Deepgram if DEEPGRAM_API_KEY set, else mock
    tts.py         text-to-speech: ElevenLabs if ELEVENLABS_API_KEY set, else mock
  llm/
    agent.py        tool-calling loop (Claude if ANTHROPIC_API_KEY set, else mock)
    tools.py        tool schemas: ask_intent, create_model, edit_model, measure,
                     check_printable, set_print_settings, print, pause, cancel, undo
    design_log.py   who-chose-what log (user vs AI) per requirement/value
  cad/
    model.py        CadQuery wrapper: named-parameter builds, STEP/STL export, undo stack
    templates.py    tested templates: plate, box, hole, keyring tag
    braille.py      one tested braille(text) -> dot positions function
  measure/
    measure.py      query CadQuery solid (size, hole dia/pos) + trimesh (wall thickness)
    checks.py       print checks: bed fit, overhangs >45°, brim-needed
  slicer/
    slice.py         prusa-slicer CLI wrapper, mock if PrusaSlicer not found
    printer.py       OctoPrint/PrusaLink client, mock printer if PRINTER_URL unset
frontend/
  index.html / app.js   push-to-talk on spacebar, screen-reader friendly, calls backend
tests/
  test_cad.py, test_measure.py, test_braille.py, test_tools.py
.env.example
requirements.txt
```

## Mock strategy
Every external integration (STT, TTS, LLM, slicer, printer) is a thin class with a real
implementation and a mock implementation; a factory picks real vs mock based on whether
the relevant env var / binary is present. Rest of the code only talks to the interface,
never to the SDK directly, so swapping in real keys at the event needs zero code changes.

## Build order
1. Voice loop (Part 1): FastAPI endpoints `/stt` and `/tts`, mock STT/TTS, push-to-talk frontend. **<- building now**
2. CadQuery templates + braille helper (Part 2 core)
3. LLM tool-calling agent wired to CadQuery tools (Part 2)
4. Measuring + print checks (Part 3)
5. Slicer + printer client, wired to settings-by-voice (Part 4)
6. Wire everything through `main.py`, end-to-end voice -> model -> print mock

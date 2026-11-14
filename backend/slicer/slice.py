"""Slicing: shell out to PrusaSlicer CLI with a saved profile. Mocked if the
PrusaSlicer binary isn't found, so the pipeline still runs end to end.
"""
import shutil
import subprocess
from pathlib import Path

PRUSA_SLICER_PATHS = [
    "/Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer",
    "prusa-slicer",
    "PrusaSlicer",
]


def _find_prusa_slicer() -> str | None:
    for candidate in PRUSA_SLICER_PATHS:
        if Path(candidate).exists() or shutil.which(candidate):
            return candidate
    return None


def slice_stl(stl_path: str, profile_path: str | None, out_path: str) -> dict:
    binary = _find_prusa_slicer()
    if binary is None:
        Path(out_path).write_text("; mock gcode -- PrusaSlicer not found\n")
        return {"gcode": out_path, "mocked": True, "estimated_minutes": 25}

    cmd = [binary, "--export-gcode", stl_path, "-o", out_path]
    if profile_path:
        cmd += ["--load", profile_path]
    subprocess.run(cmd, check=True)
    return {"gcode": out_path, "mocked": False}


def map_settings(request: str) -> dict:
    """Maps a plain-language request ('stronger', 'faster', 'finer detail')
    to slicer settings, per the voice-to-slicer-settings table in the spec."""
    request = request.lower()
    if "strong" in request:
        return {"walls": 4, "infill": 40, "note": "Stronger means 4 walls and 40% infill."}
    if "fast" in request:
        return {"layer_height": 0.3, "note": "Faster means thicker layers."}
    if "fine" in request or "detail" in request:
        return {"layer_height": 0.1, "note": "Finer detail means thinner layers."}
    return {"note": "Using default settings."}

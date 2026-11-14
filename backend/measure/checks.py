"""Print checks: bed fit, overhangs over 45 degrees, brim-needed-for-small-parts.
Every check returns a plain-language reason so Jarvis can say it out loud.
"""
import numpy as np

BED_SIZE_MM = (250.0, 210.0)  # default; override from printer profile
OVERHANG_LIMIT_DEG = 45.0
SMALL_PART_FOOTPRINT_MM2 = 400.0  # below this, add a brim


def fits_bed(bbox: dict, bed_size=BED_SIZE_MM) -> tuple[bool, str]:
    fits = bbox["length"] <= bed_size[0] and bbox["width"] <= bed_size[1]
    if fits:
        return True, "It fits easily on the bed."
    return False, (
        f"Too big for the bed: {bbox['length']}x{bbox['width']}mm "
        f"vs {bed_size[0]}x{bed_size[1]}mm."
    )


def needs_brim(bbox: dict) -> tuple[bool, str]:
    footprint = bbox["length"] * bbox["width"]
    if footprint < SMALL_PART_FOOTPRINT_MM2:
        return True, "It's small, so I added a brim so it won't come loose."
    return False, "No brim needed."


def overhangs(mesh) -> tuple[bool, str]:
    """Flags faces whose normal leans more than OVERHANG_LIMIT_DEG from vertical."""
    up = np.array([0, 0, 1])
    angles = np.degrees(np.arccos(np.clip(mesh.face_normals @ up, -1, 1)))
    bad = angles > (90 + OVERHANG_LIMIT_DEG)
    if not bad.any():
        return False, "No supports needed."
    return True, "It needs supports for some overhangs."

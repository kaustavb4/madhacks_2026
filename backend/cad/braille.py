"""One tested function: braille(text) -> list of raised-dot (x, y) positions.

Standard Braille cell spacing (ADA/NLS): dot diameter 1.5mm, dot-to-dot within
a cell 2.3mm, cell-to-cell 6.2mm, line-to-line 10mm. Supports A-Z and space.
"""

DOT_SPACING = 2.3  # mm, within a cell (horizontal and vertical)
CELL_SPACING = 6.2  # mm, between cell origins

# Each letter -> which of the 6 dots are raised, numbered:
# 1 4
# 2 5
# 3 6
BRAILLE_MAP = {
    "a": [1], "b": [1, 2], "c": [1, 4], "d": [1, 4, 5], "e": [1, 5],
    "f": [1, 2, 4], "g": [1, 2, 4, 5], "h": [1, 2, 5], "i": [2, 4], "j": [2, 4, 5],
    "k": [1, 3], "l": [1, 2, 3], "m": [1, 3, 4], "n": [1, 3, 4, 5], "o": [1, 3, 5],
    "p": [1, 2, 3, 4], "q": [1, 2, 3, 4, 5], "r": [1, 2, 3, 5], "s": [2, 3, 4], "t": [2, 3, 4, 5],
    "u": [1, 3, 6], "v": [1, 2, 3, 6], "w": [2, 4, 5, 6], "x": [1, 3, 4, 6], "y": [1, 3, 4, 5, 6],
    "z": [1, 3, 5, 6], " ": [],
}

_DOT_OFFSETS = {
    1: (0, DOT_SPACING), 4: (DOT_SPACING, DOT_SPACING),
    2: (0, 0), 5: (DOT_SPACING, 0),
    3: (0, -DOT_SPACING), 6: (DOT_SPACING, -DOT_SPACING),
}


def braille(text: str) -> list[tuple[float, float]]:
    """Return absolute (x, y) mm positions of every raised dot for `text`,
    laid out left to right starting at (0, 0)."""
    positions = []
    for i, ch in enumerate(text.lower()):
        if ch not in BRAILLE_MAP:
            raise ValueError(f"braille() has no mapping for character: {ch!r}")
        cell_x = i * CELL_SPACING
        for dot in BRAILLE_MAP[ch]:
            dx, dy = _DOT_OFFSETS[dot]
            positions.append((cell_x + dx, dy))
    return positions

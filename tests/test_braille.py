from backend.cad.braille import braille


def test_braille_known_letter():
    # 'a' is dot 1 only, at the cell origin's top-left position
    assert braille("a") == [(0.0, 2.3)]


def test_braille_unknown_char_raises():
    try:
        braille("1")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for unmapped character")


def test_braille_cells_advance():
    dots = braille("aa")
    # second 'a' cell is one CELL_SPACING to the right
    assert dots[1][0] == 6.2

"""Tested CadQuery templates, keyed by named parameters.

Each template returns (cq.Workplane solid, dict of params actually used) so
the LLM only ever supplies/edits named parameters, never raw code.
"""
import cadquery as cq

from backend.cad.braille import braille, DOT_SPACING


def plate_with_hole(length=50.0, width=20.0, thickness=3.0, hole_diameter=4.0,
                     hole_offset_x=6.0, hole_offset_y=0.0):
    """A flat plate (keyring tag base) with one through hole."""
    params = dict(length=length, width=width, thickness=thickness,
                  hole_diameter=hole_diameter, hole_offset_x=hole_offset_x,
                  hole_offset_y=hole_offset_y)
    plate = cq.Workplane("XY").box(length, width, thickness)
    plate = (
        plate.faces(">Z")
        .workplane()
        .center(-length / 2 + hole_offset_x, hole_offset_y)
        .hole(hole_diameter)
    )
    return plate, params


def box(length=50.0, width=20.0, height=10.0, wall_thickness=2.0):
    """A hollow rectangular enclosure, open on top."""
    params = dict(length=length, width=width, height=height, wall_thickness=wall_thickness)
    outer = cq.Workplane("XY").box(length, width, height)
    inner = (
        cq.Workplane("XY")
        .box(length - 2 * wall_thickness, width - 2 * wall_thickness, height - wall_thickness)
        .translate((0, 0, wall_thickness / 2))
    )
    return outer.cut(inner), params


def add_braille(solid, text, origin_x=0.0, origin_y=0.0, top_face="top",
                 dot_height=0.6, dot_diameter=1.5, plate_thickness=3.0):
    """Emboss `text` in braille on the top face of `solid`, using the one
    tested braille() layout function. Each dot is built as its own solid and
    unioned in, so the result stays a proper solid (not a stray stack item)."""
    params = dict(text=text, origin_x=origin_x, origin_y=origin_y,
                  dot_height=dot_height, dot_diameter=dot_diameter)
    z_top = solid.val().BoundingBox().zmax
    result = solid
    for dx, dy in braille(text):
        dot = (
            cq.Workplane("XY")
            .center(origin_x + dx, origin_y + dy)
            .workplane(offset=z_top)
            .circle(dot_diameter / 2)
            .extrude(dot_height)
        )
        result = result.union(dot)
    return result, params


TEMPLATES = {
    "plate_with_hole": plate_with_hole,
    "box": box,
}

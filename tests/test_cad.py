from backend.cad.model import Model
from backend.measure.measure import bounding_box, hole_info


def test_create_export_edit_undo(tmp_path):
    m = Model(export_dir=str(tmp_path))
    v = m.create("plate_with_hole", {
        "length": 50, "width": 20, "thickness": 3,
        "hole_diameter": 4, "hole_offset_x": 6,
    })
    paths = m.export("test")
    assert (tmp_path / "test.step").exists()
    assert (tmp_path / "test.stl").exists()

    bb = bounding_box(m._solid)
    assert bb == {"length": 50.0, "width": 20.0, "height": 3.0}
    assert hole_info(v.params)["diameter"] == 4

    m.edit({"length": 60})
    assert m.current.params["length"] == 60
    m.undo()
    assert m.current.params["length"] == 50

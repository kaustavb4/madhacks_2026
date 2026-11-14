"""Measuring: query the exact CadQuery solid (size, hole info) and the
exported STL via trimesh (wall thickness). Every number Jarvis speaks must
come from here -- the LLM never states a measurement itself.
"""
import numpy as np
import trimesh


def bounding_box(solid) -> dict:
    bb = solid.val().BoundingBox()
    return {
        "length": round(bb.xlen, 2),
        "width": round(bb.ylen, 2),
        "height": round(bb.zlen, 2),
    }


def hole_info(params: dict) -> dict | None:
    """Reads hole geometry straight from the named params that built the
    model, since those are the real values CadQuery used -- no re-derivation."""
    if "hole_diameter" not in params:
        return None
    return {
        "diameter": params["hole_diameter"],
        "offset_x": params.get("hole_offset_x", 0.0),
        "offset_y": params.get("hole_offset_y", 0.0),
    }


def min_wall_thickness(stl_path: str) -> float:
    """Approximate thinnest wall: ray-cast inward from each face and take the
    smallest hit distance. ponytail: naive per-face ray cast, can be fooled by
    non-manifold geometry -- swap for a proper thickness algorithm if parts
    with thin curved walls start giving bad readings."""
    mesh = trimesh.load(stl_path)
    origins = mesh.triangles_center - mesh.face_normals * 1e-3
    directions = -mesh.face_normals
    locations, index_ray, _ = mesh.ray.intersects_location(origins, directions)
    if len(locations) == 0:
        return float("nan")
    distances = np.linalg.norm(locations - origins[index_ray], axis=1)
    return round(float(distances.min()), 2)

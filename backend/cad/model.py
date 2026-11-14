"""Model: named-parameter CadQuery build + export, with an undo stack.

The LLM only ever calls create_model(template, params) / edit_model(params)
through this class -- it never writes CadQuery code directly. Every version
is appended to history so undo always works (per the design doc).
"""
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq

from backend.cad.templates import TEMPLATES, add_braille


@dataclass
class ModelVersion:
    template: str
    params: dict
    braille_text: str | None = None


class Model:
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
        self.history: list[ModelVersion] = []
        self._solid = None

    @property
    def current(self) -> ModelVersion | None:
        return self.history[-1] if self.history else None

    def create(self, template: str, params: dict, braille_text: str | None = None) -> ModelVersion:
        if template not in TEMPLATES:
            raise ValueError(f"Unknown template {template!r}, choices: {list(TEMPLATES)}")
        version = ModelVersion(template=template, params=params, braille_text=braille_text)
        self._build(version)
        self.history.append(version)
        return version

    def edit(self, params: dict) -> ModelVersion:
        """Apply partial parameter changes on top of the current version."""
        if not self.current:
            raise RuntimeError("No model to edit; call create() first.")
        merged = {**self.current.params, **params}
        version = ModelVersion(template=self.current.template, params=merged,
                                braille_text=self.current.braille_text)
        self._build(version)
        self.history.append(version)
        return version

    def undo(self) -> ModelVersion | None:
        if len(self.history) > 1:
            self.history.pop()
            self._build(self.current)
        return self.current

    def _build(self, version: ModelVersion):
        solid, _ = TEMPLATES[version.template](**version.params)
        if version.braille_text:
            solid, _ = add_braille(solid, version.braille_text)
        self._solid = solid

    def export(self, name: str = "part") -> dict[str, str]:
        if self._solid is None:
            raise RuntimeError("No model built yet.")
        step_path = self.export_dir / f"{name}.step"
        stl_path = self.export_dir / f"{name}.stl"
        cq.exporters.export(self._solid, str(step_path))
        cq.exporters.export(self._solid, str(stl_path))
        return {"step": str(step_path), "stl": str(stl_path)}

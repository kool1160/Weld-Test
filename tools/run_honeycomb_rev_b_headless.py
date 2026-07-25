#!/usr/bin/env python3
"""Build the Rev B assembly in headless FreeCAD and export real CAD files."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import FreeCAD as App
import Import

SCRIPT = Path(__file__).with_name("generate_honeycomb_rev_b.py")
spec = importlib.util.spec_from_file_location("honeycomb_generator", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load {SCRIPT}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def add_feature_headless(doc, name, label, shape, color):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "Material", "Engineering")
    obj.Material = "10-ga mild steel"
    obj.addProperty("App::PropertyLength", "NominalThickness", "Engineering")
    obj.NominalThickness = module.T
    view = getattr(obj, "ViewObject", None)
    if view is not None:
        view.ShapeColor = color
    return obj


def main() -> None:
    shapes = module.build_geometry()
    source_records = module.validate_source_shapes(shapes)

    doc = App.newDocument("LXD_Honeycomb_RevB")
    palette = [
        (0.75, 0.75, 0.75),
        (0.85, 0.55, 0.25),
        (0.45, 0.65, 0.85),
        (0.45, 0.65, 0.85),
        (0.55, 0.80, 0.55),
        (0.80, 0.70, 0.35),
        (0.80, 0.70, 0.35),
        (0.75, 0.45, 0.65),
    ]
    objects = []
    for index, (name, shape) in enumerate(shapes.items()):
        objects.append(add_feature_headless(doc, name, name.replace("_", " "), shape, palette[index]))

    doc.recompute()
    doc.saveAs(str(module.FCSTD_PATH))

    preferences = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Part/STEP")
    preferences.SetString("Scheme", "AP214")
    Import.export(objects, str(module.STEP_PATH))

    if not module.STEP_PATH.exists() or module.STEP_PATH.stat().st_size < 1000:
        raise RuntimeError("STEP export did not produce a usable file")
    if not module.FCSTD_PATH.exists() or module.FCSTD_PATH.stat().st_size < 1000:
        raise RuntimeError("Native FreeCAD save did not produce a usable file")

    source_path = module.REPORT_DIR / "HONEYCOMB_REV_B_SOURCE_SHAPES.json"
    source_path.write_text(json.dumps(source_records, indent=2), encoding="utf-8")
    App.closeDocument(doc.Name)

    print(
        json.dumps(
            {
                "status": "GENERATED",
                "source_solids": len(source_records),
                "step_file": str(module.STEP_PATH.relative_to(module.ROOT)),
                "step_size_bytes": module.STEP_PATH.stat().st_size,
                "native_file": str(module.FCSTD_PATH.relative_to(module.ROOT)),
                "native_size_bytes": module.FCSTD_PATH.stat().st_size,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

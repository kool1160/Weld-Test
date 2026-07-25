#!/usr/bin/env python3
"""Run the Rev B generator in FreeCADCmd without GUI-only ViewObject access."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import FreeCAD as App

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


module.add_feature = add_feature_headless
module.main()

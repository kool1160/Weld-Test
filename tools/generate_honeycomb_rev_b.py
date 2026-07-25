#!/usr/bin/env python3
"""Generate and validate the Rev B honeycomb GMAW hiring-test assembly.

This script must run inside FreeCAD/FreeCADCmd. Geometry is created with the
OpenCascade kernel, exported as STEP AP214, closed, and re-imported for
validation. Units inside FreeCAD are millimetres; design dimensions are inches.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import FreeCAD as App
import Import
import Part

IN = 25.4
T = 0.1345 * IN
CLEARANCE = 0.010 * IN
BUTT_GAP = 0.0625 * IN
WALL_HEIGHT = 4.0 * IN
EPS = 0.02 * IN

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "cad" / "assembly" / "rev-b"
NATIVE_DIR = ROOT / "cad" / "native-freecad" / "rev-b"
REPORT_DIR = ROOT / "documents" / "prototype-validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)
NATIVE_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

STEP_PATH = OUT_DIR / "LXD_10GA_GMAW_HONEYCOMB_REV_B_ASSEMBLY.step"
FCSTD_PATH = NATIVE_DIR / "LXD_10GA_GMAW_HONEYCOMB_REV_B_ASSEMBLY.FCStd"
REPORT_PATH = REPORT_DIR / "HONEYCOMB_REV_B_STEP_VALIDATION.json"
REPORT_MD_PATH = REPORT_DIR / "HONEYCOMB_REV_B_STEP_VALIDATION.md"


def inch(value: float) -> float:
    return value * IN


def vec2(point: tuple[float, float]) -> App.Vector:
    return App.Vector(inch(point[0]), inch(point[1]), 0.0)


def polygon_prism(points_in: list[tuple[float, float]], z: float, height: float) -> Part.Shape:
    points = [App.Vector(inch(x), inch(y), z) for x, y in points_in]
    points.append(points[0])
    wire = Part.makePolygon(points)
    return Part.Face(wire).extrude(App.Vector(0, 0, height))


def transform_local(shape: Part.Shape, origin: App.Vector, angle_deg: float) -> Part.Shape:
    result = shape.copy()
    result.Placement = App.Placement(origin, App.Rotation(App.Vector(0, 0, 1), angle_deg))
    return result


def line_data(p1_in: tuple[float, float], p2_in: tuple[float, float]):
    p1 = vec2(p1_in)
    p2 = vec2(p2_in)
    delta = p2.sub(p1)
    length = math.hypot(delta.x, delta.y)
    angle = math.degrees(math.atan2(delta.y, delta.x))
    return p1, p2, length, angle


def oriented_slot(
    p1_in: tuple[float, float],
    p2_in: tuple[float, float],
    distance_in: float,
    tab_width_in: float,
    z0: float,
    height: float,
) -> Part.Shape:
    p1, _, _, angle = line_data(p1_in, p2_in)
    theta = math.radians(angle)
    center = App.Vector(
        p1.x + inch(distance_in) * math.cos(theta),
        p1.y + inch(distance_in) * math.sin(theta),
        z0,
    )
    length = inch(tab_width_in) + CLEARANCE
    width = T + CLEARANCE
    local = Part.makeBox(length, width, height, App.Vector(-length / 2, -width / 2, 0))
    return transform_local(local, center, angle)


def make_vertical_plate(
    p1_in: tuple[float, float],
    p2_in: tuple[float, float],
    bottom_tabs: list[tuple[float, float]],
    top_tabs: list[tuple[float, float]],
    trim_max_y_in: float | None = None,
) -> Part.Shape:
    p1, _, length, angle = line_data(p1_in, p2_in)
    body_local = Part.makeBox(length, T, WALL_HEIGHT, App.Vector(0, -T / 2, T))
    shape = transform_local(body_local, p1, angle)

    for distance_in, tab_width_in in bottom_tabs:
        width = inch(tab_width_in)
        tab_local = Part.makeBox(width, T, T, App.Vector(inch(distance_in) - width / 2, -T / 2, 0))
        shape = shape.fuse(transform_local(tab_local, p1, angle))

    for distance_in, tab_width_in in top_tabs:
        width = inch(tab_width_in)
        tab_local = Part.makeBox(
            width,
            T,
            T,
            App.Vector(inch(distance_in) - width / 2, -T / 2, T + WALL_HEIGHT),
        )
        shape = shape.fuse(transform_local(tab_local, p1, angle))

    if trim_max_y_in is not None:
        max_y = inch(trim_max_y_in)
        clip = Part.makeBox(inch(30), inch(30), inch(10), App.Vector(-inch(15), -inch(15), -inch(1)))
        clip = clip.common(
            Part.makeBox(inch(30), max_y + inch(15), inch(10), App.Vector(-inch(15), -inch(15), -inch(1)))
        )
        shape = shape.common(clip)

    return shape.removeSplitter()


def shape_record(name: str, shape: Part.Shape) -> dict:
    bounds = shape.BoundBox
    return {
        "name": name,
        "valid": bool(shape.isValid()),
        "solids": len(shape.Solids),
        "volume_mm3": round(shape.Volume, 3),
        "bounds_mm": {
            "x": round(bounds.XLength, 3),
            "y": round(bounds.YLength, 3),
            "z": round(bounds.ZLength, 3),
        },
    }


def add_feature(doc, name: str, label: str, shape: Part.Shape, color: tuple[float, float, float]):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "Material", "Engineering").Material = "10-ga mild steel"
    obj.addProperty("App::PropertyLength", "NominalThickness", "Engineering").NominalThickness = T
    obj.ViewObject.ShapeColor = color
    return obj


def build_geometry():
    # Octagonal base gives the assembly a compact structural-node footprint.
    base_outline = [
        (-3.0, -3.0),
        (3.0, -3.0),
        (4.0, -2.0),
        (4.0, 1.0),
        (3.0, 3.0),
        (-3.0, 3.0),
        (-4.0, 1.0),
        (-4.0, -2.0),
    ]

    back_line = ((-3.0, 3.0), (3.0, 3.0))
    left_line = ((-4.0, -1.0), (-3.0, 3.0 - (T / 2 + EPS) / IN))
    right_line = ((3.0, 3.0 - (T / 2 + EPS) / IN), (4.0, -1.0))
    web_line = ((0.75, -1.0), (0.75, 3.0 - (T / 2 + EPS) / IN))

    back_bottom = [(1.10, 0.45), (4.25, 0.65)]
    back_top = [(1.35, 0.55), (4.50, 0.45)]
    left_bottom = [(1.00, 0.50), (3.00, 0.65)]
    left_top = [(1.45, 0.50), (3.25, 0.45)]
    right_bottom = [(0.80, 0.55), (2.90, 0.45)]
    right_top = [(1.00, 0.60), (2.80, 0.50)]
    web_bottom = [(0.90, 0.45), (2.60, 0.60)]
    web_top = [(1.20, 0.45), (3.00, 0.55)]

    base = polygon_prism(base_outline, 0, T)
    for line, tabs in [
        (back_line, back_bottom),
        (left_line, left_bottom),
        (right_line, right_bottom),
        (web_line, web_bottom),
    ]:
        for distance, width in tabs:
            slot = oriented_slot(line[0], line[1], distance, width, -EPS, T + 2 * EPS)
            base = base.cut(slot)
    base = base.removeSplitter()

    back = make_vertical_plate(back_line[0], back_line[1], back_bottom, back_top)
    left = make_vertical_plate(left_line[0], left_line[1], left_bottom, left_top, trim_max_y_in=3.0 - (T / 2 + EPS) / IN)
    right = make_vertical_plate(right_line[0], right_line[1], right_bottom, right_top, trim_max_y_in=3.0 - (T / 2 + EPS) / IN)
    web = make_vertical_plate(web_line[0], web_line[1], web_bottom, web_top, trim_max_y_in=3.0 - (T / 2 + EPS) / IN)

    # Split top cap creates a genuine coplanar square-butt joint with a 1/16-in gap.
    cap_outline = [(-4.0, -1.0), (4.0, -1.0), (3.0, 3.0), (-3.0, 3.0)]
    cap = polygon_prism(cap_outline, T + WALL_HEIGHT, T)
    for line, tabs in [
        (back_line, back_top),
        (left_line, left_top),
        (right_line, right_top),
        (web_line, web_top),
    ]:
        for distance, width in tabs:
            slot = oriented_slot(
                line[0],
                line[1],
                distance,
                width,
                T + WALL_HEIGHT - EPS,
                T + 2 * EPS,
            )
            cap = cap.cut(slot)

    split_left = Part.makeBox(
        inch(20),
        inch(20),
        inch(10),
        App.Vector(-inch(20), -inch(10), -inch(1)),
    )
    split_left = split_left.common(
        Part.makeBox(
            inch(20) - BUTT_GAP / 2,
            inch(20),
            inch(10),
            App.Vector(-inch(20), -inch(10), -inch(1)),
        )
    )
    split_right = Part.makeBox(
        inch(20),
        inch(20),
        inch(10),
        App.Vector(BUTT_GAP / 2, -inch(10), -inch(1)),
    )
    cap_left = cap.common(split_left).removeSplitter()
    cap_right = cap.common(split_right).removeSplitter()

    # Front lap plate overlaps the base by 1.5 in and carries two plug-weld holes.
    lap = Part.makeBox(inch(6.0), inch(2.0), T, App.Vector(-inch(3.0), -inch(3.5), T))
    for x_in in (-1.5, 1.5):
        hole = Part.makeCylinder(inch(0.375) / 2, T + 2 * EPS, App.Vector(inch(x_in), inch(-2.35), T - EPS))
        lap = lap.cut(hole)
    lap = lap.removeSplitter()

    return {
        "G_BASE": base,
        "A_BACK_WALL": back,
        "B_LEFT_ANGLED_WALL": left,
        "E_RIGHT_ANGLED_WALL": right,
        "C_OFFSET_INNER_WEB": web,
        "D1_LEFT_TOP_CAP": cap_left,
        "D2_RIGHT_TOP_CAP": cap_right,
        "F_FRONT_LAP_PLATE": lap,
    }


def validate_source_shapes(shapes: dict[str, Part.Shape]) -> list[dict]:
    records = [shape_record(name, shape) for name, shape in shapes.items()]
    for record in records:
        if not record["valid"]:
            raise RuntimeError(f"Invalid OpenCascade shape: {record['name']}")
        if record["solids"] != 1:
            raise RuntimeError(f"Expected one solid for {record['name']}, got {record['solids']}")
        if record["volume_mm3"] <= 0:
            raise RuntimeError(f"Zero-volume shape: {record['name']}")
    return records


def main() -> None:
    shapes = build_geometry()
    source_records = validate_source_shapes(shapes)

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
        objects.append(add_feature(doc, name, name.replace("_", " "), shape, palette[index]))

    doc.recompute()
    doc.saveAs(str(FCSTD_PATH))

    step_preferences = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Part/STEP")
    step_preferences.SetString("Scheme", "AP214")
    Import.export(objects, str(STEP_PATH))

    if not STEP_PATH.exists() or STEP_PATH.stat().st_size < 1000:
        raise RuntimeError("STEP export did not produce a usable file")

    App.closeDocument(doc.Name)

    # Independent close/re-open check through the same OpenCascade importer.
    Import.open(str(STEP_PATH))
    imported_doc = App.ActiveDocument
    imported_records = []
    total_solids = 0
    for obj in imported_doc.Objects:
        if not hasattr(obj, "Shape") or obj.Shape.isNull():
            continue
        record = shape_record(obj.Label or obj.Name, obj.Shape)
        imported_records.append(record)
        total_solids += record["solids"]
        if not record["valid"]:
            raise RuntimeError(f"Re-imported invalid shape: {record['name']}")

    if total_solids != 8:
        raise RuntimeError(f"Re-imported STEP contains {total_solids} solids; expected 8")

    report = {
        "status": "PASS",
        "generator": "FreeCAD/OpenCascade",
        "step_protocol": "AP214",
        "material": "10-ga mild steel",
        "nominal_thickness_in": 0.1345,
        "slot_clearance_total_in": 0.010,
        "butt_gap_in": 0.0625,
        "source_shape_count": len(source_records),
        "reimported_solid_count": total_solids,
        "step_file": str(STEP_PATH.relative_to(ROOT)),
        "native_file": str(FCSTD_PATH.relative_to(ROOT)),
        "step_file_size_bytes": STEP_PATH.stat().st_size,
        "source_shapes": source_records,
        "reimported_shapes": imported_records,
        "solidworks_verification": "Not available in GitHub Actions; STEP was closed and re-opened with OpenCascade.",
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    rows = "\n".join(
        f"| {item['name']} | {item['solids']} | {item['volume_mm3']:.3f} | "
        f"{item['bounds_mm']['x']} × {item['bounds_mm']['y']} × {item['bounds_mm']['z']} | {item['valid']} |"
        for item in source_records
    )
    REPORT_MD_PATH.write_text(
        "# Honeycomb Rev B STEP validation\n\n"
        "- **Status:** PASS\n"
        "- **CAD kernel:** FreeCAD/OpenCascade\n"
        "- **STEP protocol:** AP214\n"
        "- **Material thickness:** 0.1345 in\n"
        "- **Nominal butt gap:** 0.0625 in\n"
        "- **Total imported solids after close/re-open:** 8\n"
        "- **SolidWorks verification:** Not run in GitHub Actions.\n\n"
        "| Component | Solids | Volume mm³ | Bounding box mm | Valid |\n"
        "|---|---:|---:|---|---|\n"
        f"{rows}\n\n"
        "This remains a prototype design. It must be opened in SolidWorks and physically dry-fitted before production release.\n",
        encoding="utf-8",
    )

    App.closeDocument(imported_doc.Name)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

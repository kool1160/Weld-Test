#!/usr/bin/env python3
"""Re-open the exported Rev B STEP in a fresh FreeCAD/OpenCascade process."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[1]
STEP_PATH = ROOT / "cad" / "assembly" / "rev-b" / "LXD_10GA_GMAW_HONEYCOMB_REV_B_ASSEMBLY.step"
FCSTD_PATH = ROOT / "cad" / "native-freecad" / "rev-b" / "LXD_10GA_GMAW_HONEYCOMB_REV_B_ASSEMBLY.FCStd"
REPORT_DIR = ROOT / "documents" / "prototype-validation"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_JSON = REPORT_DIR / "HONEYCOMB_REV_B_STEP_VALIDATION.json"
REPORT_MD = REPORT_DIR / "HONEYCOMB_REV_B_STEP_VALIDATION.md"
SOURCE_JSON = REPORT_DIR / "HONEYCOMB_REV_B_SOURCE_SHAPES.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not STEP_PATH.exists() or STEP_PATH.stat().st_size < 1000:
        raise RuntimeError(f"Missing or empty STEP file: {STEP_PATH}")
    if not FCSTD_PATH.exists() or FCSTD_PATH.stat().st_size < 1000:
        raise RuntimeError(f"Missing or empty native CAD file: {FCSTD_PATH}")

    # Part.read uses the OpenCascade exchange reader without creating an OCAF
    # document. This avoids the known FreeCAD 0.19 ImportOCAF2 crash while still
    # performing a genuine fresh-process STEP parse and B-rep reconstruction.
    imported = Part.read(str(STEP_PATH))
    if imported is None or imported.isNull():
        raise RuntimeError("OpenCascade returned a null shape from STEP")

    total_solids = len(imported.Solids)
    valid = bool(imported.isValid())
    solid_records = []
    for index, solid in enumerate(imported.Solids, start=1):
        box = solid.BoundBox
        solid_records.append(
            {
                "index": index,
                "valid": bool(solid.isValid()),
                "volume_mm3": round(solid.Volume, 3),
                "bounds_mm": {
                    "x": round(box.XLength, 3),
                    "y": round(box.YLength, 3),
                    "z": round(box.ZLength, 3),
                },
            }
        )

    errors = []
    if total_solids != 8:
        errors.append(f"Expected 8 solids, found {total_solids}")
    if not valid:
        errors.append("Imported compound is not a valid OpenCascade shape")
    for record in solid_records:
        if not record["valid"]:
            errors.append(f"Solid {record['index']} is invalid")
        if record["volume_mm3"] <= 0:
            errors.append(f"Solid {record['index']} has zero volume")

    source_records = []
    if SOURCE_JSON.exists():
        source_records = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))

    report = {
        "status": "PASS" if not errors else "FAIL",
        "generator": "FreeCAD 0.19 / OpenCascade",
        "validation_method": "Fresh FreeCADCmd process using Part.read STEP parser",
        "step_protocol": "AP214",
        "material": "10-ga mild steel",
        "nominal_thickness_in": 0.1345,
        "nominal_slot_clearance_total_in": 0.010,
        "nominal_butt_gap_in": 0.0625,
        "step_file": str(STEP_PATH.relative_to(ROOT)),
        "native_file": str(FCSTD_PATH.relative_to(ROOT)),
        "step_file_size_bytes": STEP_PATH.stat().st_size,
        "step_sha256": sha256(STEP_PATH),
        "native_file_size_bytes": FCSTD_PATH.stat().st_size,
        "native_sha256": sha256(FCSTD_PATH),
        "source_shape_count": len(source_records),
        "reopened_solid_count": total_solids,
        "reopened_compound_valid": valid,
        "reopened_solids": solid_records,
        "errors": errors,
        "solidworks_verification": "Not run in GitHub Actions. Chris must open the prototype in SolidWorks before release.",
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    rows = "\n".join(
        f"| {item['index']} | {item['volume_mm3']:.3f} | "
        f"{item['bounds_mm']['x']} × {item['bounds_mm']['y']} × {item['bounds_mm']['z']} | {item['valid']} |"
        for item in solid_records
    )
    error_text = "None" if not errors else "; ".join(errors)
    REPORT_MD.write_text(
        "# Honeycomb Rev B STEP validation\n\n"
        f"- **Status:** {report['status']}\n"
        "- **Generator:** FreeCAD 0.19 / OpenCascade\n"
        "- **STEP protocol:** AP214\n"
        "- **Validation:** Closed after export and reopened in a fresh FreeCADCmd process with `Part.read()`\n"
        f"- **Reopened solids:** {total_solids}\n"
        f"- **Compound valid:** {valid}\n"
        f"- **Errors:** {error_text}\n"
        f"- **STEP SHA-256:** `{report['step_sha256']}`\n"
        "- **SolidWorks verification:** Required before fabrication release.\n\n"
        "| Solid | Volume mm³ | Bounding box mm | Valid |\n"
        "|---:|---:|---|---|\n"
        f"{rows}\n\n"
        "This is a prototype assembly, not a released laser-cut hiring-test package.\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))
    if errors:
        raise RuntimeError("; ".join(errors))


if __name__ == "__main__":
    main()

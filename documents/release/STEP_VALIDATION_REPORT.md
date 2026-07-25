# STEP Validation Report

## Build configuration

- CAD software: CadQuery 2.8.0
- CAD kernel: OpenCascade 7.9.3.1
- DXF reader: ezdxf 1.4.4
- Authoritative geometry: `laser/dxf-parts/WT-001` through `WT-012`
- Export protocol: AP214
- Model/export units: millimeters
- Material thickness: 0.135 in (3.429 mm)
- Close/reopen method: build process exited; a separate validation process reopened every exported STEP with OpenCascade

## Individual STEP results

| Generated filename | Solids | Bounding dimensions, in (X x Y x Z) | Thickness, in | Reopen | Topology/faces | Mesh |
|---|---:|---:|---:|---|---|---|
| `cad/parts/WT-001_BASE.step` | 1 | 12.000000 x 12.000000 x 0.135000 | 0.135000 | PASS | PASS | None |
| `cad/parts/WT-002_SPINE.step` | 1 | 10.000000 x 4.500000 x 0.135000 | 0.135000 | PASS | PASS | None |
| `cad/parts/WT-003_CROSS.step` | 1 | 10.000000 x 4.500000 x 0.135000 | 0.135000 | PASS | PASS | None |
| `cad/parts/WT-004_VERTICAL.step` | 1 | 3.000000 x 6.500000 x 0.135000 | 0.135000 | PASS | PASS | None |
| `cad/parts/WT-005_CORNER_A.step` | 1 | 3.000000 x 4.500000 x 0.135000 | 0.135000 | PASS | PASS | None |
| `cad/parts/WT-006_CORNER_B.step` | 1 | 3.500000 x 4.500000 x 0.135000 | 0.135000 | PASS | PASS | None |
| `cad/parts/WT-007_LAP_LOWER.step` | 1 | 4.000000 x 3.500000 x 0.135000 | 0.135000 | PASS | PASS | None |
| `cad/parts/WT-008_LAP_UPPER.step` | 1 | 4.000000 x 3.000000 x 0.135000 | 0.135000 | PASS | PASS | None |
| `cad/parts/WT-009_BUTT_A.step` | 1 | 5.000000 x 2.000000 x 0.135000 | 0.135000 | PASS | PASS | None |
| `cad/parts/WT-010_BUTT_B.step` | 1 | 5.000000 x 2.000000 x 0.135000 | 0.135000 | PASS | PASS | None |
| `cad/parts/WT-011_GAP_GAUGE.step` | 1 | 3.000000 x 1.000000 x 0.135000 | 0.135000 | PASS | PASS | None |
| `cad/parts/WT-012_SLOT_COUPON.step` | 1 | 4.000000 x 1.500000 x 0.135000 | 0.135000 | PASS | PASS | None |

## Assembly STEP result

- Generated filename: `cad/assembly/LXD_10GA_MIG_WELD_TEST_ASSEMBLY.step`
- Solid-body/component count: 10 / 10
- Intended components: `WT-001_BASE`, `WT-002_SPINE`, `WT-003_CROSS`, `WT-004_VERTICAL`, `WT-005_CORNER_A`, `WT-006_CORNER_B`, `WT-007_LAP_LOWER`, `WT-008_LAP_UPPER`, `WT-009_BUTT_A`, `WT-010_BUTT_B`
- Bounding dimensions: 18.000000 x 12.000000 x 6.500000 in (X x Y x Z)
- OpenCascade close/reopen result: PASS
- Topology and all faces: PASS
- Component-volume match to individual STEP files: PASS
- Intended product names present: PASS
- Mesh bodies: none
- Zero-volume bodies: none

## Native CAD sources

- Rebuild source: `cad/source/rebuild_weld_test.py`
- Individual OpenCascade BREP files: `cad/native/parts/*.brep`
- Assembly OpenCascade XCAF/BREP files: `cad/native/assembly/*.xbf`, `cad/native/assembly/*.brep`
- Build provenance: `cad/native/build-metadata.json`

## SolidWorks verification

PASS - SOLIDWORKS Design Professional for Makers 2026 SP2.0 opened the AP214 assembly successfully after export and kernel validation. The imported assembly displayed all ten WT-001 through WT-010 components, with no import-error dialog or missing-component warning. The reopened document was then closed without saving a converted native copy.

## Remaining warnings

- The controlled package provides a concept view and assembly sequence but no dimensioned assembly-coordinate drawing. Placement follows the etched stations and stated fit-up values.
- WT-006 contains four exact duplicate coincident CUT lines. They are removed only in the temporary import copy.
- Revision A remains a prototype subject to slot-coupon and complete physical dry-assembly verification.

## Overall result

**PASS** - all STEP files closed, reopened, and passed OpenCascade B-Rep validation.

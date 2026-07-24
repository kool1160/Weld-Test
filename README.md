# Weld-Test

Laser-cut, poka-yoke MIG weld test for evaluating new-hire and production welding skills.

## Current design basis

- Material: 10-gauge mild steel
- Process: GMAW / MIG
- Assembly: laser-cut tab-and-slot construction
- Purpose: internal workmanship and skill evaluation
- Status: Revision A prototype

> This repository is an internal production weld-test project. It is not an AWS welder qualification package unless reviewed and administered under the applicable code by qualified personnel.

## Repository structure

```text
cad/
  assembly/          Assembled STEP and native CAD files
  parts/             Individual 3D part models
laser/
  dxf-parts/         Individual 1:1 laser-cut DXF profiles
  nests/             Sheet nests and machine-ready layouts
drawings/
  assembly/          Assembly and weld-map drawings
  parts/             Individual part drawings
documents/
  instructions/      Candidate instructions and setup sheets
  inspection/        Inspection forms and scoring sheets
  release/           Released document packages and manifests
reference/            Photos, sketches, standards notes, and research
archive/              Superseded or obsolete revisions
```

## File naming

Use the following pattern where practical:

```text
WT-###_DESCRIPTION_REV-X.ext
```

Examples:

```text
WT-100_BASE_REV-A.dxf
WT-200_WELD-TEST-ASSEMBLY_REV-A.step
WT-300_WELD-TEST-PACKAGE_REV-A.pdf
```

## Revision control

- Keep work-in-progress files out of `documents/release/`.
- Released files must use a visible revision.
- Do not overwrite a released revision; create the next revision.
- Move superseded releases to `archive/`.
- Record material thickness, slot width, actual sheet thickness, and laser fit-test results before production release.

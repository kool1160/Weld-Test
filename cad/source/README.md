# Validated STEP rebuild

`rebuild_weld_test.py` imports the authoritative `CUT` geometry from the
individual DXFs, scales the inch profiles to millimeters, and builds
0.135-inch solids with CadQuery/OpenCascade.

Run the build and validation in separate processes so every STEP file is
closed before it is reopened:

```powershell
python cad/source/rebuild_weld_test.py build
python cad/source/rebuild_weld_test.py validate
```

The build writes AP214 STEP files plus native OpenCascade BREP/XBF sources.
The validation command reopens every STEP file and writes
`documents/release/STEP_VALIDATION_REPORT.md`.

The script removes exact duplicate `CUT` line entities in memory before
kernel import. The authoritative DXF files are never modified.

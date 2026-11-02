# 0005 — Altium Designer as the MADpilot-H7 EDA tool

The PCB Design Engineer's professional tool of choice is Altium Designer, and routing proficiency beats tool licensing at solo scale. MADpilot-H7 schematic capture and PCB layout therefore move from KiCad to Altium Designer; the KiCad Rev A capture is tagged `kicad-revA` in git history and removed from the tree, while the frozen RevA BOM and `MADpilot-H7-RevA-Schematics.pdf` remain the valid Rev A records and the design content itself is unchanged.

## Considered Options

- **Stay on KiCad** — rejected: the engineer who owns the 6-layer layout and DFM works fastest in Altium; tool friction at the layout stage costs more than the license difference.
- **Import the KiCad capture via Altium's importer** — rejected: no PCB layout ever existed (only schematic capture), so a fresh native capture from the Rev A requirements checklist and the pin plan (comparative-review.md §7) is cheaper and yields a clean Altium-native project.

## Consequences

- CERN-OHL-S-2.0 Corresponding Source at publication means the editable Altium project files (`.PrjPcb` / `.SchDoc` / `.PcbDoc`), not solely Gerbers or PDFs (release/design-files/README.md updated accordingly).
- The KiCad S-expression schematic tests were retired; Rev A requirements live in `docs/hardware/rev-a-schematic-requirements.md`, and `tests/test_reva_bom_requirements.py` validates the frozen RevA BOM in a tool-agnostic way (Altium BOM CSV exports fit the same format).
- `scripts/snapshot_bom.py` consumes Altium BOM CSV exports from now on; the snapshot workflow itself is unchanged and immutable.
- The planned Altium project structure mirrors the retired KiCad hierarchy: `MADpilot-H7.PrjPcb` with root `MADpilot-H7.SchDoc` instantiating POWER, MCU, SENSORS, CAN, STORAGE, CONNECTORS, DEBUG sheets, plus `MADpilot-H7.PcbDoc`.
- The Rev A Altium capture is a prerequisite for the refreshed G0 review package.

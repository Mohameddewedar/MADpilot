# Release Staging — Hardware Design Files

This directory is the staging area for hardware design publication packages released under the **CERN Open Hardware Licence Version 2 - Strongly Reciprocal (CERN-OHL-S-2.0)**.

Per [ADR-0001](../../docs/adr/0001-open-hardware-license-path.md), while the project is in personal/educational development and nothing is distributed, design files remain private. The moment any Flight Controller unit is sold or publicly distributed, complete corresponding design files must be published under CERN-OHL-S-2.0.

> **Note on Project Phase:**
> In Phase 0, active hardware design has not yet started and the top-level `hardware/` design directory does not exist yet (scheduled for Phase 1 per [PLAN.md](../../PLAN.md)). When hardware design begins in Phase 1, `release/design-files/` serves as the staging location where frozen, verifiable release archives are assembled prior to publication at sale.

---

## What Gets Published at Sale

When a release is activated for sale or public distribution, this directory publishes a clean, complete, standalone archive of the hardware design:

1. **KiCad Project Sources**:
   - Project file (`.kicad_pro`)
   - Schematic files (`.kicad_sch`)
   - PCB layout files (`.kicad_pcb`)
   - Custom schematic symbols, footprint libraries, and 3D models used in the design

2. **Bill of Materials (BOM)**:
   - Complete KiCad BOM in CSV format
   - Per-part procurement records and assembly house part numbers (matching the In-Stock-First snapshot)

3. **Manufacturing & Fabrication Outputs**:
   - Gerber fabrication files (RS-274X / Gerber X2)
   - Excellon NC drill files
   - Pick-and-place component placement files (Centroid / CPL format)
   - PCB assembly drawings and layer stackup specifications

---

## CERN-OHL-S-2.0 Attribution & Reciprocity Obligations

The MADpilot-H7 hardware design derives from open hardware reference designs (specifically SAL-FC as primary baseline per [ADR-0003](../../docs/adr/0003-base-design-sal-fc-primary.md), with LEVIA-H7 as cross-check). Consequently, any public distribution or sale entails strict compliance with CERN-OHL-S-2.0:

1. **Complete Source Making Available (Section 3)**:
   - You must make available the complete Corresponding Source (the editable KiCad files) to anyone who receives the physical hardware or design files.
   - The source must be provided in the preferred format for making modifications (KiCad format, not solely Gerbers or PDFs).

2. **Attribution Notices (Section 4)**:
   - All existing copyright, author attribution, and license notices from upstream designs (SAL-FC, LEVIA-H7) must be preserved intact.
   - Any modifications made for MADpilot-H7 must be clearly identified with prominent notices stating that the design has been modified, describing the nature of the modifications, and recording the modification date and author.

3. **License Text Co-Distribution (Section 3.1)**:
   - Every distribution of the design files, and every physical unit transferred or sold, must be accompanied by a copy of the license text located at [release/licenses/CERN-OHL-S-2.0.txt](../licenses/CERN-OHL-S-2.0.txt) and the notices required by the license.

4. **Hardware Marking Notice**:
   - Where feasible, the PCB silkscreen and accompanying packaging must include the CERN-OHL-S-2.0 notice and a pointer to the repository where Corresponding Source can be obtained.

---

## Trademark Policy

In strict accordance with [ADR-0001](../../docs/adr/0001-open-hardware-license-path.md):
- "Pixhawk" is never used in or adjacent to the product name. The product is named strictly **MADpilot-H7**.
- References to "Pixhawk" in documentation, schematics, or packaging appear solely in factual compatibility statements (e.g. connector standard compatibility per [ADR-0002](../../docs/adr/0002-pixhawk-standard-connectors.md)).

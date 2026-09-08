# 0003 — Base design: SAL-FC primary, LEVIA-H7 cross-check

MADpilot-H7 derives from SAL-FC (KiCad, STM32H743, 6-layer, CERN-OHL-S-2.0, documented as built at JLCPCB) with LEVIA-H7 as a comparative second opinion during the Phase-1 schematic review — rather than designing from scratch or cloning legacy Pixhawk files.

## Considered Options

- **Clean original design to the FMUv6C standard** — rejected under ADR-0001 economics: roughly doubles Phase 1 for IP exclusivity the project doesn't need.
- **Legacy Pixhawk clone (Pixracer/FMUv4)** — rejected: 2015-era STM32F427, EAGLE/Altium sources, dead-end technology.
- **LEVIA-H7 as primary** — viable; SAL-FC's JLC-procurement BOM and documented JLCPCB build won the tie.

## Consequences

- Two independent H743 designs get diffed during review — catches solo-designer blind spots.
- CERN-OHL-S-2.0 publication obligation attaches at sale (ADR-0001).
- Sensor substitutions per In-Stock-First are expected modifications (ICM-42605 + BMI270 for the out-of-stock BMI088 and stock-flaky ICM-42688-P).

## Amendment — LEVIA-H7 promoted to primary (2026-09-07)

In August 2026, the SAL-FC team moved all KiCad design files, Gerbers, BOM, and CPL into a private repository ahead of a commercial v2 release. Only firmware target files (`hwdef.dat`, `hwdef-bl.dat`), pinout tables, and PCB renders remain public. The original premise of ADR-0003 — forking SAL-FC's native `.kicad_sch` and `.kicad_pcb` files — is no longer viable without requesting private access and accepting potential confidentiality terms.

**Amended decision:** LEVIA-H7 is now the **Base Design** (primary EDA starting point). MADpilot-H7's KiCad project is a fresh project adapting LEVIA-H7's open schematics from TFBGA-100 to LQFP-176, with Pixhawk-standard connectors (ADR-0002) replacing LEVIA's quad-copter ESC topology. SAL-FC is retained as a firmware-mapping and power-architecture reference using its public `hwdef.dat` and pinout documentation.

**Why not request SAL-FC private access?** Introduces an external dependency, potential delay, and confidentiality terms that could complicate immediate Sell-Ready status under ADR-0001. LEVIA-H7 is 100% open (CERN-OHL-S-2.0), immediately actionable, and provides complete KiCad 10 schematics, PCB layout, and JLCPCB manufacturing packages.

**Consequences of the amendment:**
- The comparative review methodology still diffs two independent H743 designs — only the roles are swapped.
- CERN-OHL-S-2.0 attribution for LEVIA-H7 is required in the MADpilot-H7 project metadata and schematic title blocks.
- The TFBGA-100 → LQFP-176 package adaptation is the primary schematic capture effort; the pin plan (comparative-review.md §7) already maps all signals to LQFP-176.

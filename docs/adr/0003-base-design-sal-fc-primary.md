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

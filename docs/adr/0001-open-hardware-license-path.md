# 0001 — Open-hardware license path (publish on sale)

The project is personal/educational now but must stay Sell-Ready at any moment. Deriving the Flight Controller from CERN-OHL-S-2.0 designs (SAL-FC / LEVIA-H7) is compatible with that only if selling triggers publication of the modified design files. We accept that: the product ships open — design files published at sale, ArduPilot GPLv3 source offered alongside — and Sell-Ready's release checklist includes staging that publication.

## Considered Options

- **Clean original design** (publication never required) — rejected: roughly doubles Phase 1 for IP exclusivity the project doesn't need, since the firmware must be GPL-offered at sale regardless.
- **Derive now, clean rev later** — rejected: silently breaks Sell-Ready for Rev A/B, which would only ever be sellable with publication anyway.

## Consequences

- No obligation exists while nothing is distributed; education-phase boards stay private by default.
- The moment any board is sold: modified KiCad sources are published under CERN-OHL-S-2.0, and the exact ArduPilot firmware source used is offered per GPLv3.
- Trademark rule: the product is never marketed with "Pixhawk" in its name; "Pixhawk" appears only in compatibility statements.

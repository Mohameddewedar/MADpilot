# MADpilot

A personal/educational project manufacturing a fixed-wing flight controller from open Pixhawk/ArduPilot data, engineered to remain sellable at any moment.

## Language

**Flight Controller (FC)**:
The manufactured circuit board together with its compiled firmware. The product of the current phase.
_Avoid_: autopilot, flight computer

**Autopilot System**:
A Flight Controller plus its carrier board, GNSS/compass module, and power module — a complete pilotage package. Candidate scope for the next phase.

**Sell-Ready**:
The standing requirement that the project could be sold as-is at any moment: license-compliant, trademark-safe name, unique board/USB identity, certification-ready design, GPLv3 source offer in place.
_Avoid_: commercial-ready

**Phase Gate**:
A hard pass/fail criterion that must be met before work advances to the next manufacturing phase.

**Improvement Backlog**:
The ordered list of design deltas versus the chosen reference board, each tagged with the phase gate at which it is decided or dropped.

**Rev**:
A hardware revision of the Flight Controller. Rev A is the first prototype; Rev B is the first assembled small batch.

**MADpilot-H7**:
The Flight Controller's board model — one identity across the hwdef directory, firmware string, bootloader board ID, and product name.

**In-Stock-First**:
The rule that a design may only freeze when every BOM part is procurable from the chosen assembly house at that moment. A Sell-Ready property.

**Reference Board**:
The Pixhawk 6C — the standard every Improvement Backlog delta is measured against.
_Avoid_: clone target, baseline

**Radio Allowance**:
The standing pre-approved radio bands: 433 MHz, 915 MHz, 2.4 GHz, 5 GHz. Any other band is assumed allowed until confirmed with the project owner.

**Outsource-on-Stall**:
The policy of outsourcing a checkpoint only once it has stalled, rather than by pre-plan.

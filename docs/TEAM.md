# Team & Roles

Solo-professional core with an on-demand pool. One person may hold several roles; nothing here assumes a standing organization.

| Role | Holder | Cost | Notes |
|---|---|---|---|
| Hardware lead | Project owner | — | Professional PCB/KiCad |
| Firmware lead | Project owner | — | Professional embedded C/C++ |
| Flight-test pilots | Ready pool | Mostly free | Available now; also witness flight Phase Gates (G3–G7) |
| External reviewer (gate G0) | **TBD** — identify before schematic capture completes | $0–300 | Mandatory schematic + layout review before the Rev A order |
| Outsource pool | Per checkpoint | Mostly free, occasionally paid | Engaged per the Outsource-on-Stall policy |

## G0 External Reviewer — Placeholder

**Position:** Independent Hardware Design Reviewer (contract, one-time engagement)

**Role:** Provide an independent technical review of the MADpilot-H7 Rev A schematic and PCB layout *before* the first PCBA order is placed. The reviewer acts as the single mandatory external gate between design completion and fabrication spend. They have no ongoing obligations beyond the G0 deliverable.

**Tasks:**
1. Receive and review the complete G0 Review Package (schematic PDFs, BOM CSV with stock verification, pin-plan table, Reference Board delta document, and KiCad project files if requested).
2. Verify schematic correctness: power sequencing, decoupling, sensor bus assignments, protection circuits, and connector pinouts against DS-018 / ADR-0002.
3. Review PCB layout: stackup, impedance-controlled traces (USB, SDMMC), ground plane integrity under IMUs, thermal relief on power components, DFM clearances for JLCPCB 6-layer.
4. Deliver a written findings report (pass / conditional-pass / fail) with itemised issues ranked by severity.
5. Optionally participate in one follow-up session to clarify findings.

**Selection criteria:** Experience with STM32H7-class flight controllers or high-density mixed-signal PCBs; familiarity with JLCPCB/LCSC manufacturing constraints preferred. Candidates: ArduPilot Hardware Discord community, freelance PCB reviewers (Upwork/Fiverr), or university contacts with embedded-systems lab experience.

## Outsource-on-Stall

- A checkpoint that stalls (about a week with no progress) is handed off — to the free pool, or paid if needed — or explicitly parked with a written swap decision. Silent spinning is the only forbidden move.
- The cost estimate carries a contingency line for the paid case.

## Predicted first hand-offs

1. Rev A layout review (fresh eyes on stackup, decoupling, IMU placement)
2. Bring-up debugging if Rev A fails to boot or a sensor stays dead
3. Carrier-board mechanical design (Phase 2+, if the Autopilot System proceeds)

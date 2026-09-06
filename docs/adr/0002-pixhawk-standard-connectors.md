# 0002 — Pixhawk-standard connector set

MADpilot-H7 adopts the Pixhawk-standard connector set and placement (DS-018-style: POWER1/2, USB-C, TELEM1/2, GPS1/2, I2C, CAN1/2, PWM-OUT, SBUS/PPM, Spektrum/RSSI, safety switch, buzzer) instead of solder pads or a hybrid layout. A labeled SWD header and boot/DFU button are kept for bring-up.

## Considered Options

- **Solder pads (Matek-style)** — rejected: cheaper, but strands the board outside the COTS ecosystem (GNSS pucks, power modules, telemetry radios, carriers).
- **Hybrid (standard connectors, custom placement)** — rejected: tends to mate with nothing; placement is part of the standard.

## Consequences

- Higher BOM per board (JST-GH connectors), accepted.
- The next-phase Autopilot System gets a defined mating surface for its carrier board — the main reason for this decision.
- Ethernet (H743 MAC present) is deliberately deferred to the Improvement Backlog: it drags in PHY, magnetics, and a jack the current scope doesn't need.

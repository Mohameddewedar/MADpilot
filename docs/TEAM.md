# Team & Roles

Solo-professional core with an on-demand pool. One person may hold several roles; nothing here assumes a standing organization.

| Role | Holder | Cost | Notes |
|---|---|---|---|
| Hardware lead | Project owner | — | Professional PCB/KiCad |
| Firmware lead | Project owner | — | Professional embedded C/C++ |
| Flight-test pilots | Ready pool | Mostly free | Available now; also witness flight Phase Gates (G3–G7) |
| External reviewer (gate G0) | Community or paid | $0–300 | Mandatory schematic + layout review before the Rev A order |
| Outsource pool | Per checkpoint | Mostly free, occasionally paid | Engaged per the Outsource-on-Stall policy |

## Outsource-on-Stall

- A checkpoint that stalls (about a week with no progress) is handed off — to the free pool, or paid if needed — or explicitly parked with a written swap decision. Silent spinning is the only forbidden move.
- The cost estimate carries a contingency line for the paid case.

## Predicted first hand-offs

1. Rev A layout review (fresh eyes on stackup, decoupling, IMU placement)
2. Bring-up debugging if Rev A fails to boot or a sensor stays dead
3. Carrier-board mechanical design (Phase 2+, if the Autopilot System proceeds)

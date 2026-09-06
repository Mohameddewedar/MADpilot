# MADpilot — Manufacturing Plan

Personal/educational manufacture of **MADpilot-H7**, a fixed-wing flight controller derived from open Pixhawk/ArduPilot data — kept **Sell-Ready** at all times. 12-month program, solo-professional core (TEAM.md), budget $1,650–2,870 (COST-ESTIMATE.md).

Companions: `CONTEXT.md` (language) · `docs/adr/` (decisions 0001–0004) · `EQUIPMENT.md` (procurement) · `TEAM.md` (roles).

## Program overview

| Phase | Window | Goal | Exit gate |
|---|---|---|---|
| Phase 0 — Learn | M0–M2 | Dev-kit flying; fork + CI running; design underway | dev board flies stabilized; CI green |
| Phase 1 — Rev A | M2–M6 | First custom board brought up | G0 order review, G1, G2 |
| Phase 2 — Rev B | M6–M12 | Small batch; full autonomous mission | G3–G9 |
| Phase 3 — Scale (optional) | M12+ | Batch >50, Autopilot System, or sale | per option below |

## Phase 0 — Learn (M0–M2)

- Buy: Matek H743-Wing, GNSS puck, SiK 433 + 915 MHz, ESP32 bridge, bench gap-fill (EQUIPMENT.md).
- Firmware: fork ArduPilot on GitHub, branch off **stable Plane**; hub repo + submodule layout (ADR-0004); CI building `./waf plane` apj from day one; OEM layer (`defaults.parm`, `AP_CUSTOM_FIRMWARE_STRING "MADpilot"`); builds on native Linux (Ubuntu LTS).
- Design study: SAL-FC vs LEVIA-H7 comparative schematic review (ADR-0003); draft MADpilot-H7 sensor/connector plan (ICM-42605 + BMI270, MS5611, Pixhawk-standard connectors per ADR-0002).
- Fly: test plane on the H743-Wing through the ladder up to G6 — decouples "learning ArduPilot plane" from "debugging my own board".
- Identity prep: board-ID PR (see action items), pid.codes application.

## Phase 1 — Rev A (M2–M6)

- Derive the KiCad project from SAL-FC, LEVIA as cross-check; **In-Stock-First** BOM freeze (ICM-42605, BMI270, MS5611, STM32H743 LQFP-176).
- Custom board support: `hwdef/MADpilotH7/hwdef.dat` + `hwdef-bl.dat`, `APJ_BOARD_ID 3141`, USB VID 0x1D50 + pid.codes PID; bootloader via `Tools/scripts/build_bootloaders.py`, flashed by SWD.
- **G0: mandatory external schematic + layout review** before ordering (proactive, on top of the reactive Outsource-on-Stall policy).
- Order: JLC 6-layer bare x10 + stencil + turnkey PCBA x5; hand-build one education board from a spare bare (hotplate + stencil).
- Bring-up against G1/G2; **Sim-on-Hardware** (`Tools/scripts/sitl-on-hardware/sitl-on-hw.py`) before any taxi attempt.

## Phase 2 — Rev B (M6–M12)

- Fix list from Rev A; Rev B order (turnkey x5–10).
- Mount in the test plane; flight ladder G3–G8 with pilots witnessing.
- Decide backlog entries gated here (#3 onboard mag — only if the GNSS-puck compass limits performance; #6 cost-down variant).
- Exit **G9** → choose Phase 3.

## Phase 3 — Scale (optional, M12+), cheapest-first

1. **Batch >50**: JLC standard PCBA, panelization, DFM/DFT review, first-article inspection of 3–5 units.
2. **Autopilot System**: carrier board + GNSS + power module — the next-phase scope from Round 1; connector standard (ADR-0002) already defines the mating surface.
3. **Sale**: triggers design-file publication (CERN-OHL-S-2.0, ADR-0001), ArduPilot GPLv3 source offer, and the deferred Sell-Ready items below.

## Phase gates

- **G0** external schematic + layout review passed (before any Rev A order)
- **G1** bench bring-up: boots via SWD, bootloader flashed, GCS link over USB and telemetry, all sensors live, actuator sweep
- **G2** Rev A complete: full sensor set logging on a vibration-realistic mount, no brownouts, current draw within budget
- **G3** taxi · **G4** manual flight · **G5** FBWA + airspeed calibrated · **G6** autotune
- **G7** full autonomous mission including failsafes (RTL on link loss, battery failsafe)
- **G8** three consecutive clean missions → freeze Rev B
- **G9** Rev B flies a clean mission → batches >50 permitted

## Improvement Backlog (decided at gates, never before)

| # | Entry | Gate |
|---|---|---|
| 1 | Ethernet (H743 MAC + PHY) | after Rev B flies |
| 2 | Third IMU / second baro | Rev C |
| 3 | Onboard magnetometer | Rev C, only if GNSS-puck compass limits flight performance |
| 4 | Integrated power module / carrier with PM | Phase-2 Autopilot System decision |
| 5 | Ruggedized variant (temp, vibration, IP) | evidence of real-world or sale interest |
| 6 | Cost-down variant | after three clean Rev B missions |

## Sell-Ready checklist

**Prep-now (cheap; skipping them is the irreversible part):**
- Board ID **3141** reserved via PR to `Tools/AP_Bootloader/board_types.txt` — `AP_HW_MADPILOT_H7 3141` inside a **3136–3145** ten-ID zone centered on pi (the file's convention caps block reservations at 10 IDs per PR); ODID variant (if ever) = 13141.
- pid.codes PID under VID **0x1D50**.
- Trademark-safe naming records; "Pixhawk" never in the product name (compatibility statements only).
- `release/` staging area: design-file publication package (CERN-OHL-S-2.0) + ArduPilot source offer.
- In-Stock-First BOM snapshots archived at every rev freeze.

**Defer-until-sale (expensive):**
- CE / FCC / RoHS testing ($3k–10k).
- Egypt sale-legality review (drone-adjacent regulation; a domestic buyer base changes the exposure).
- Pricing and per-unit economics finalization (COST-ESTIMATE.md has the draft).

## Egypt operating rules

- **Import — accurate and boring**: a bare FC PCB is declared as what it is ("assembled printed circuit board / electronic development board"); radios never co-ship with FC parcels; LiPos local only; assume 14% VAT + 0–10% duty, no de-minimis; parcels below USD 2,000 / 50 kg avoid ACID pre-registration; drone license + Radio Allowance documents kept ready if customs asks.
- **Radio Allowance**: 433 / 915 MHz / 2.4 / 5 GHz pre-approved; any other band confirmed with the project owner before ordering.
- **Flying**: under the held drone license / ECAA aero-club arrangement; pilots witness flight gates G3–G7.

## Risks

| Risk | Mitigation |
|---|---|
| Sensor stock drift (BMI088 gone; ICM-42688-P flaky) | In-Stock-First at every rev freeze; second sources pre-listed |
| First-board DOA | G0 external review; SWD + inspection microscope; hand-built spare board |
| Customs seizure | Accurate-and-boring declarations; never co-ship radios; license docs ready |
| Solo stall | Outsource-on-Stall (TEAM.md) + contingency line in the cost estimate |
| EGP / CBE card-cap volatility | Split orders across months; wire alternative; recheck at every purchase |
| Board-ID collision on PR day | Re-verify the live `board_types.txt`; fallback gaps 1178 / 1153 / 1249 |

## Action items (now)

1. PR to `board_types.txt`: reserve **3136–3145** — 3141 = MADpilot-H7, remainder = variant zone (10-ID cap per the file's convention; re-verify the live file first). Additional 10-blocks only via later PRs, when variants actually enter design.
2. Apply to pid.codes for a PID under 0x1D50.
3. Ask the license issuer: does the permit cover equipment import, or operation only?
4. Order Phase-0 hardware (EQUIPMENT.md).
5. Set up the fork + hub repo + CI (ADR-0004).
6. Begin the SAL-FC / LEVIA comparative review.

# Equipment & Procurement List

12-month program. Prices are 2026 estimates in USD (EGP ~50/USD, volatile — recheck at purchase; check the bank's CBE international-spend cap before large orders). Sources: **local** = Cairo shops (RAM Electronics, Future Electronics, UGE, Micro Ohm, Hobby25); **LCSC** = via JLCPCB assembly; **AliExpress** = where local/LCSC is unavailable.

## Bench — verify ownership before buying; much may already be owned

| Item | Source | Est. | Note |
|---|---|---|---|
| ST-Link V2 (SWD) | local (~290 EGP) or clone | $5 | First purchase. Non-negotiable for bootloader flashing and bring-up |
| Bench PSU 30 V / 5 A | local (UNI-T class) | $60 | Verify owned |
| DMM | local (DT830 199 EGP … UT-class ~4,275 EGP) | $25 | Verify owned |
| Reflow hotplate | AliExpress | $40 | For the hand-built education board (one of the extra bare Rev A boards) |
| Solder/rework station incl. hot air | — | — | Verify owned |
| Inspection microscope or USB cam | AliExpress | $60 | 0402/LGA joint inspection; strongly recommended |
| Tweezers, flux, paste syringe, wick, wire | local/AliExpress | $35 | Consumables for the hand-build |
| Logic analyzer (LA1010/DSLogic class) | AliExpress | $30 | Optional: UART/SPI/I2C debug |

## Test fleet

| Item | Source | Est. | Note |
|---|---|---|---|
| Foam trainer aircraft | OWNED | — | Test planes in hand; pilots ready (TEAM.md) |
| Spare props, servos, linkages | local RC shops | $60 | Crash-consumable budget |
| LiPo batteries + charger | local | $80 | Air-import of LiPos is effectively prohibited — local only |
| RC transmitter + receivers | OWNED (verify) | — | Spektrum binding port gets exercised if a Spektrum RX is used |
| GNSS puck, M9N-class | AliExpress/LCSC | $35 | Compass source for Rev A (no onboard mag) |
| SiK telemetry, 433 MHz (Holybro V3 class) | AliExpress | $60 | Radio Allowance band |
| SiK telemetry, 915 MHz (Holybro V3 class) | AliExpress | $60 | Radio Allowance band — kept per Round-3 decision |
| ESP32 WiFi MAVLink bridge | local (UGE, ~675 EGP) | $10 | Bench telemetry; 2.4 GHz per Radio Allowance |
| Airspeed sensor (MS4525 / SDP3x) | AliExpress | $30 | Fixed-wing phase, gate G5+ |

## Phase-0 dev board — pending Round-4 decision

| Option | Est. | Note |
|---|---|---|
| Matek H743-Wing | ~$80 | Recommended: same MCU family as MADpilot-H7, plane-native, in-tree hwdef |
| Pixhawk 6C | ~$200 | Connector-standard experience; doubles as a physical Reference Board |

## Fabrication, per board revision (JLCPCB)

| Item | Est. (per rev) | Note |
|---|---|---|
| 6-layer bare PCBs x10 | $60–120 | Run the quote before freezing Phase-1 budget |
| Laser-cut stencil | $3–8 | |
| Economic PCBA turnkey x5 | $250–420 incl. parts | In-Stock-First BOM; BMI088 is out of stock — ICM-42605 + BMI270 substitution |
| DHL shipping to Egypt | $30–60 | |
| Egypt import (14% VAT + 0–10% duty on CIF + clearance fee) | $60–120 | Assume no de-minimis; below USD 2,000 / 50 kg no ACID pre-registration needed |

## Radio & shipping notes

- Bands inside the Radio Allowance (433/915/2.4/5 GHz) are pre-approved; any other radio part is assumed allowed but is confirmed with the project owner before ordering.
- NTRA import type-approval for radio modules is unverified — prefer local sourcing for radios where possible; radios are never co-shipped with FC parcels.
- Parcel declaration policy: set by the Round-4 decision (Q26).

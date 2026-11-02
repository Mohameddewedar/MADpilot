# MADpilot-H7 Rev A Schematic Requirements (Altium Redraw Checklist)

**Purpose:** The tool-neutral statement of every requirement the Rev A schematic capture must satisfy. The Altium Designer capture (per [ADR-0005](../adr/0005-altium-eda-tool.md)) must implement all of them.

**Provenance:** Extracted from the retired KiCad S-expression test suite (git tag `kicad-revA`) at the EDA tool switch. The Rev A design content is unchanged. Machine-checkable invariants (parts, LCSC numbers, quantities) are validated against the frozen RevA BOM by `tests/test_reva_bom_requirements.py`; the connectivity items below are checked at schematic review until Altium netlist exports are wired into CI.

**Authoritative pin plan:** [comparative-review.md §7](comparative-review.md).

---

## 1. Project Structure

- Altium project `MADpilot-H7.PrjPcb`.
- Root schematic `MADpilot-H7.SchDoc` instantiating 7 hierarchical sheets: **POWER, MCU, SENSORS, CAN, STORAGE, CONNECTORS, DEBUG** (pages 1–8 total).
- PCB layout `MADpilot-H7.PcbDoc` (6-layer, JLC06161H-3313 stackup per TEAM.md).
- Preserve LEVIA-H7 / piecol / CERN-OHL-S-2.0 attribution in project metadata and schematic title blocks, as well as the hardware README and root LICENSE (ADR-0003).
- Before routing, meet the [Altium capture and placement gate](rev-a-design-gates.md#capture-to-routing), including ERC evidence, requirements traceability and BOM reconciliation. The historical KiCad PDF and BOM are reference records, not proof of the Altium capture's completion.

## 2. MCU Sheet

- STM32H743IIT6, LQFP-176 package, LCSC **C89597**.
- Dual 2.2 µF low-ESR VCAP capacitors for the internal regulator.
- Decoupling: at least 8× 100 nF on VDD; 10 nF + 1 µF on VDDA/VREF+.
- 8.000 MHz quartz crystal (NX3225GD-8MHZ-STD-CRA-3, LCSC **C889706**) on `OSC_IN`/`OSC_OUT` with 2× 15 pF C0G load capacitors; standard active crystal drive — no HSE bypass (`STM32_HSE_BYPASS` omitted in hwdef).
- NRST circuit: pull-up resistor, 100 nF filter capacitor, reset pushbutton.
- BOOT0 circuit: 10 kΩ pull-down plus boot pushbutton to 3.3 V.

### MCU net labels and pin-plan traceability

Use the schematic interface labels below. Trace every connection to the same MCU pin and peripheral in `hwdef/MADpilotH7/hwdef.dat` and comparative-review.md §7; firmware/peripheral and connector-facing labels may have different spellings. The following alias map makes those names explicit for USB, I2C, RSSI and VBUS; the completed capture checklist supplies sheet/net/reference evidence for all connections.

| Schematic net | Connector-facing pin-plan signal | MCU pin | Firmware pin label |
|---|---|---|---|
| `OTG_FS_DP` | `USB_DP` | PA12 | `OTG_FS_DP` |
| `OTG_FS_DM` | `USB_DM` | PA11 | `OTG_FS_DM` |
| `RSSI_ADC` | `RSSI_IN` | PC2 | `RSSI_ADC` |
| `GPS_SCL` | `GPS1_SCL` and `GPS2_SCL` (one shared bus) | PB8 | `I2C1_SCL` |
| `GPS_SDA` | `GPS1_SDA` and `GPS2_SDA` (one shared bus) | PB9 | `I2C1_SDA` |
| `BARO_SCL` | `BARO_SCL` | PB10 | `I2C2_SCL` |
| `BARO_SDA` | `BARO_SDA` | PB11 | `I2C2_SDA` |
| `EXT_I2C_SCL` | `EXT_I2C_SCL` | PF14 | `I2C4_SCL` |
| `EXT_I2C_SDA` | `EXT_I2C_SDA` | PF15 | `I2C4_SDA` |
| `VBUS_DETECT` | `VBUS` sense | PA9 | `VBUS` |

- IMU buses: `IMU1_SCK`, `IMU1_MISO`, `IMU1_MOSI`, `IMU1_CS`, `IMU1_DRDY`; `IMU2_SCK`, `IMU2_MISO`, `IMU2_MOSI`, `IMU2_CS`, `IMU2_DRDY`
- I2C: `BARO_SCL`, `BARO_SDA`, `GPS_SCL`, `GPS_SDA`, `EXT_I2C_SCL`, `EXT_I2C_SDA`
- CAN: `FDCAN1_RX`, `FDCAN1_TX`, `FDCAN2_RX`, `FDCAN2_TX`
- Serial: `GPS1_TX`, `GPS1_RX`, `GPS2_TX`, `GPS2_RX`, `TELEM1_TX`, `TELEM1_RX`, `TELEM1_CTS`, `TELEM1_RTS`, `TELEM2_TX`, `TELEM2_RX`, `TELEM2_CTS`, `TELEM2_RTS`, `RC_TX`, `RC_RX`
- PWM actuators: `PWM1` … `PWM12`
- ADC: `VOLTAGE1`, `CURRENT1`, `VOLTAGE2`, `CURRENT2`, `RSSI_ADC`
- USB: `OTG_FS_DM`, `OTG_FS_DP`, `VBUS_DETECT`
- MicroSD: `SDMMC1_D0`, `SDMMC1_D1`, `SDMMC1_D2`, `SDMMC1_D3`, `SDMMC1_CK`, `SDMMC1_CMD`
- Safety: `SAFETY_SW`, `SAFETY_LED`, `BUZZER`

## 3. POWER Sheet

- AP63205WU-7 5 V 2 A synchronous buck (LCSC **C2071056**) with input filtering, 2.2 µH power inductor (SRP4020TA-2R2M, **C231647**), and output filter capacitors.
- AO3407A P-FET reverse-polarity protection (LCSC **C15127**) plus SMAJ30CA TVS clamp on battery input (LCSC **C81938**).
- Dual 1N5819WS Schottky diode OR-ing (LCSC **C8598**, qty ≥ 2) between USB VBUS and the 5 V buck output.
- AP7343-33W5-7 low-noise LDO → `3V3_SENS` rail (LCSC **C460383**).
- AP2112K-3.3TRG1 LDO → `3V3_MCU` rail (LCSC **C51118**).
- Rails labeled `3V3_SENS` and `3V3_MCU`.

## 4. SENSORS Sheet

- Primary IMU: TDK ICM-42605 (LCSC **C2655099**, LGA-14) on SPI1, nets `IMU1_*`.
- Secondary IMU: Bosch BMI270 (LCSC **C2836813**, LGA-14) on SPI4, nets `IMU2_*`.
- Barometer: MS561101BA03-50 (LCSC **C15639**) on I2C2, nets `BARO_SCL` / `BARO_SDA`.
- All sensors powered from `3V3_SENS` with decoupling (≥ 4 capacitors, including the 10 µF filter and ferrite bead).
- **Strictly no onboard magnetometer** (QMC5883, HMC5883, IST8310, LIS3MDL, MMC5983 — external GNSS-puck compass only; onboard gated to Rev C).

## 5. CAN Sheet

- CAN1 transceiver: SN65HVD230DR (LCSC **C12084**, SOIC-8).
- CAN2 transceiver: SIT1051ATK/3 (LCSC **C5382552**, DFN-8).
- MCU nets: `FDCAN1_TX`, `FDCAN1_RX`, `FDCAN2_TX`, `FDCAN2_RX`.
- Per bus: 120 Ω termination resistor (LCSC **C22787**, qty ≥ 2) with a solder jumper for termination selection (LCSC **C371752**, qty ≥ 2).
- PESD2CAN ESD protection arrays on the differential lines (LCSC **C18214**, qty ≥ 2).
- Bus lines `CAN1_H` / `CAN1_L` / `CAN2_H` / `CAN2_L` to 4-pin JST-GH connectors.

## 6. STORAGE Sheet

- TF-01A push-push MicroSD socket (LCSC **C91145**) on 4-bit SDMMC1 (`SDMMC1_D0`–`D3`, `CK`, `CMD`).
- 10 kΩ pull-ups on data/command lines (qty ≥ 5) and rail decoupling.
- Powered from `3V3_MCU`.

## 7. CONNECTORS Sheet (DS-018 per ADR-0002)

- POWER1 & POWER2: 6-pin JST-GH with `VOLTAGE1`/`CURRENT1`/`VOLTAGE2`/`CURRENT2` sense.
- TELEM1 & TELEM2: 6-pin JST-GH with RTS/CTS hardware flow control.
- GPS1: 10-pin JST-GH (`GPS1_TX`, `GPS1_RX`, `GPS_SCL`, `GPS_SDA`, `SAFETY_SW`, `SAFETY_LED`, `BUZZER`); GPS2: 6-pin JST-GH (`GPS2_TX`, `GPS2_RX`, shared external I2C).
- External I2C: 4-pin JST-GH (`EXT_I2C_SCL`, `EXT_I2C_SDA`); RC_IN: 5-pin JST-GH (`RC_RX`, `RSSI_ADC`, `RC_TX`).
- USB-C: TYPE-C-31-M-12 receptacle (LCSC **C165948**), 2× 5.1 kΩ CC pull-downs, `VBUS_DETECT`, USBLC6-2P6 ESD clamp (LCSC **C15999**); nets `OTG_FS_DM` / `OTG_FS_DP`.
- 12-channel PWM servo rail headers (`PWM1` … `PWM12`) grouped by timer banks.

## 8. DEBUG Sheet

- 4-pin SWD header: `3V3_MCU`, `SWDIO`, `SWCLK`, `GND`.

## 9. Frozen Rev A BOM Invariants

- The historical Rev A BOM has 40 line items / 107 component instances across the 7 sheets.
- Every critical part carries the exact LCSC number listed above; validated by `tests/test_reva_bom_requirements.py` against `hardware/bom/MADpilot-H7-RevA-bom.csv` (immutable snapshot: `hardware/bom/snapshots/RevA-2026-09-08/`).
- Reconcile the new Altium export against that historical BOM by manufacturer part number, LCSC number, quantity, footprint and references (including a reference-renumbering map). Record and approve every difference; the historical BOM checks do not validate Altium connectivity or a new export by themselves.

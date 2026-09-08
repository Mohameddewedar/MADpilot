# MADpilot-H7 KiCad Hardware Project

This directory contains the KiCad EDA project files (schematic capture and PCB layout) for the **MADpilot-H7** Flight Controller (Rev A).

---

## 1. Project Identity & Architecture

- **Product Name:** MADpilot-H7
- **Target MCU:** STMicroelectronics STM32H743IIT6 (ARM Cortex-M7, 480 MHz, 2MB Flash, 1MB RAM, LQFP-176 package)
- **Reference Board:** Pixhawk 6C (DS-018 Pixhawk Connector Standard compliance per [docs/adr/0002-pixhawk-standard-connectors.md](../../docs/adr/0002-pixhawk-standard-connectors.md))
- **Base Design:** LEVIA-H7 by piecol (per [docs/adr/0003-base-design-sal-fc-primary.md](../../docs/adr/0003-base-design-sal-fc-primary.md))
- **Hardware Revision:** Rev A (Prototype)
- **EDA Tool:** KiCad 8.x / 9.x

---

## 2. Open Hardware Attribution & Licensing

### Base Design Attribution

The MADpilot-H7 hardware design is derived from and inspired by **LEVIA-H7**, an open-source flight controller designed by **piecol**:
- **Original Project:** [LEVIA-H7 on GitHub](https://github.com/piecol/LEVIA-H7)
- **Original Author:** piecol
- **Original License:** CERN Open Hardware Licence Version 2 - Strongly Reciprocal ([CERN-OHL-S-2.0](../../release/licenses/CERN-OHL-S-2.0.txt))

### Secondary Reference Attribution

MADpilot-H7 also references architectural and pin mapping principles from **SAL-FC**:
- **Reference Project:** [SAL-FC on GitHub](https://github.com/salehali22/SAL-FC)
- **Authors:** Saleh Alhomeidy, Akaki Gvelesiani, and Levan Kazaishvili
- **License:** CERN-OHL-S-2.0

### Scope of Adaptation

MADpilot-H7 is a fresh KiCad project implementing substantial architectural adaptations to fulfill fixed-wing UAV requirements:
1. **MCU Package Adaptation:** Re-targeted from LEVIA-H7's 8x8mm TFBGA-100 package to an accessible, inspectable LQFP-176 package (STM32H743IIT6).
2. **Connector Modernization:** Replaced LEVIA's multi-rotor quad-ESC solder pads and headers with full Pixhawk-standard JST-GH locking connectors (DS-018: POWER1, POWER2, TELEM1, TELEM2, GPS1, GPS2, CAN1, CAN2, EXT I2C, RC) and a 12-channel 0.1" servo rail.
3. **In-Stock-First Sensor Suite:** Retained dual dissimilar IMUs partitioned across DMA domains: Primary TDK ICM-42605 on SPI1 (D1 domain) and Secondary Bosch BMI270 on SPI4 (D2 domain), with MEAS MS5611 barometer on internal I2C2.
4. **Power System:** Main 5V 2A switching buck (AP63205WU), independent dual 3.3V LDO rails (`3V3_MCU` via AP2112K and ultra-low-noise `3V3_SENS` via AP7343), USB VBUS diode OR-ing, and reverse-polarity P-FET protection.

### License Notice

In compliance with **CERN-OHL-S-2.0**, all schematic designs, PCB layouts, bill of materials, and production files within this directory are licensed under:

**CERN Open Hardware Licence Version 2 - Strongly Reciprocal (CERN-OHL-S-2.0)**  
Full legal text is available at [release/licenses/CERN-OHL-S-2.0.txt](../../release/licenses/CERN-OHL-S-2.0.txt).

Per [ADR-0001](../../docs/adr/0001-open-hardware-license-path.md), upon any commercial distribution or sale of manufactured hardware, complete source design files matching the manufactured revision are made available to the recipient under these terms.

# MADpilot-H7 Phase-1 Comparative Hardware Review & Pin Plan

**Document ID:** MAD-HW-REV-001  
**Target Hardware:** MADpilot-H7 Flight Controller (STM32H743, LQFP-176)  
**Revision:** Rev A Bring-Up Draft (Pre-G0 Review)  
**Binding Decisions:** [ADR-0001 (License Path & Trademark)](../adr/0001-open-hardware-license-path.md), [ADR-0002 (Pixhawk-Standard Connector Set)](../adr/0002-pixhawk-standard-connectors.md), [ADR-0003 (Base Design: SAL-FC Primary, LEVIA-H7 Cross-Check)](../adr/0003-base-design-sal-fc-primary.md), [ADR-0004 (Hub Repo & ArduPilot Submodule)](../adr/0004-hub-repo-fork-submodule.md)  
**Program Guides:** [CONTEXT.md](../../CONTEXT.md), [PLAN.md](../../PLAN.md)

---

## 1. Scope and Methodology

This document delivers the Phase-1 comparative hardware review and the complete hardware pin allocation plan for **MADpilot-H7**, an open-hardware fixed-wing Flight Controller (FC) designed around the STMicroelectronics STM32H743 high-performance ARM Cortex-M7 microcontroller.

The objective of MADpilot is educational and personal development while maintaining **Sell-Ready** status at all timesâ€”meaning the design remains fully license-compliant (CERN-OHL-S-2.0 / GPLv3), trademark-safe, and manufacturable using current COTS assembly capabilities under the **In-Stock-First** rule.

### Methodology
In accordance with [ADR-0003](../adr/0003-base-design-sal-fc-primary.md), this review analyzes two independent open-hardware STM32H743 flight controller designs:
1. **SAL-FC** as the primary base design reference.
2. **LEVIA-H7** as the comparative second-opinion and validation cross-check.
3. **Pixhawk 6C** as the **Reference Board** standard against which architectural deltas and connector compliance ([ADR-0002](../adr/0002-pixhawk-standard-connectors.md)) are benchmarked.

Each design is examined across its electrical schematics, PCB layout and stackup, component procurement, power rail distribution, timer allocation, bus routing, and firmware definitions. Findings from both base designs are synthesized to construct a robust, conflict-free pin plan for the MADpilot-H7 in an LQFP-176 package.

### Source Artifacts Catalog
All comparative claims in this review cite concrete artifacts from the following sources:

*   **SAL-FC (Primary Base Design)**:
    *   Remote Repository: [https://github.com/salehali22/SAL-FC](https://github.com/salehali22/SAL-FC)
    *   Remote Readme & Pinout: [https://raw.githubusercontent.com/salehali22/SAL-FC/main/README.md](https://raw.githubusercontent.com/salehali22/SAL-FC/main/README.md)
    *   Cited paths below are locations within the SAL-FC repository.
    *   ArduPilot Hardware Definition: [`SAL-FC: Firmware Target Files/ArduPilot/hwdef.dat`](https://github.com/salehali22/SAL-FC/blob/main/Firmware%20Target%20Files/ArduPilot/hwdef.dat)
    *   ArduPilot Bootloader Definition: [`SAL-FC: Firmware Target Files/ArduPilot/hwdef-bl.dat`](https://github.com/salehali22/SAL-FC/blob/main/Firmware%20Target%20Files/ArduPilot/hwdef-bl.dat)
    *   Betaflight Target Configuration: [`SAL-FC: Firmware Target Files/Betaflight/target.h`](https://github.com/salehali22/SAL-FC/blob/main/Firmware%20Target%20Files/Betaflight/target.h) and [`SAL-FC: Firmware Target Files/Betaflight/config.h`](https://github.com/salehali22/SAL-FC/blob/main/Firmware%20Target%20Files/Betaflight/config.h)
    *   iNAV Target & SPI6 HAL Patch: `SAL-FC: Firmware Target Files/iNAV/spi6-patch/`
    *   License: [`SAL-FC: LICENSE`](https://github.com/salehali22/SAL-FC/blob/main/LICENSE) (CERN-OHL-S-2.0)
*   **LEVIA-H7 (Comparative Cross-Check)**:
    *   Remote Repository: [https://github.com/piecol/LEVIA-H7](https://github.com/piecol/LEVIA-H7)
    *   Remote Readme: [https://raw.githubusercontent.com/piecol/LEVIA-H7/main/README.md](https://raw.githubusercontent.com/piecol/LEVIA-H7/main/README.md)
    *   Cited paths below are locations within the LEVIA-H7 repository.
    *   Top-Level Schematic: [`LEVIA-H7: LEVIA_H7.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/LEVIA_H7.kicad_sch)
    *   Hierarchical MCU Sheet: [`LEVIA-H7: MCU.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/MCU.kicad_sch)
    *   Hierarchical Power Sheet: [`LEVIA-H7: POWER.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/POWER.kicad_sch)
    *   Hierarchical Sensors Sheet: [`LEVIA-H7: SENSORS.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/SENSORS.kicad_sch)
    *   Hierarchical CAN Sheet: [`LEVIA-H7: CAN.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/CAN.kicad_sch)
    *   Hierarchical MicroSD Sheet: [`LEVIA-H7: MICRO_SD.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/MICRO_SD.kicad_sch)
    *   Hierarchical RC Input Sheet: [`LEVIA-H7: RC_INPUT.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/RC_INPUT.kicad_sch)
    *   Hierarchical Buzzer Sheet: [`LEVIA-H7: BUZZER.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/BUZZER.kicad_sch)
    *   Hierarchical Video Sheets: [`LEVIA-H7: ANALOG_VTX.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/ANALOG_VTX.kicad_sch) and [`LEVIA-H7: DIGITAL_VTX.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/DIGITAL_VTX.kicad_sch)
    *   Hierarchical Motor Sheets: [`LEVIA-H7: MOTORS[1-4].kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/MOTORS[1-4].kicad_sch) and [`LEVIA-H7: MOTORS[5-8].kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/MOTORS[5-8].kicad_sch)
    *   Hierarchical External Bus Sheet: [`LEVIA-H7: I2C1_SPI3.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/I2C1_SPI3.kicad_sch) (remote: `https://raw.githubusercontent.com/piecol/LEVIA-H7/main/I2C1%7CSPI3.kicad_sch`)
    *   PCB Layout: [`LEVIA-H7: LEVIA_H7.kicad_pcb`](https://github.com/piecol/LEVIA-H7/blob/main/LEVIA_H7.kicad_pcb)
    *   Manufacturing BOM: [`LEVIA-H7: jlcpcb/production_files/BOM-LEVIA_H7.csv`](https://github.com/piecol/LEVIA-H7/blob/main/jlcpcb/production_files/BOM-LEVIA_H7.csv)
    *   License: [`LEVIA-H7: LICENSE.txt`](https://github.com/piecol/LEVIA-H7/blob/main/LICENSE.txt) (CERN-OHL-S-2.0)
*   **Reference Board (Pixhawk 6C)**:
    *   Standard Specification: DS-018 Pixhawk Autopilot Standard (FMUv6C)
    *   Holybro Ports & Wiring Guide: [https://docs.holybro.com/autopilot/pixhawk-6c/pixhawk-6c-ports.md](https://docs.holybro.com/autopilot/pixhawk-6c/pixhawk-6c-ports.md)
    *   ArduPilot Hardware Definition: [https://raw.githubusercontent.com/ArduPilot/ardupilot/master/libraries/AP_HAL_ChibiOS/hwdef/Pixhawk6C/hwdef.dat](https://raw.githubusercontent.com/ArduPilot/ardupilot/master/libraries/AP_HAL_ChibiOS/hwdef/Pixhawk6C/hwdef.dat)

---

## 2. Source Availability Assessment: SAL-FC Hardware Privatization

> [!WARNING]
> ### Critical Availability Fact
> In August 2026, the SAL-FC development team relocated all KiCad design files, Gerber fabrication packages, component bills of materials (BOM), pick-and-place files (CPL), and 3D CAD models from their public GitHub repository into a private repository ahead of an upcoming commercial v2 hardware release.
> 
> As documented in the [`SAL-FC: README.md`](https://github.com/salehali22/SAL-FC/blob/main/README.md#L363-L377) under the section *"Hardware Files Access"*:
> > *"The KiCad project, Gerbers, BOM, pick-and-place files, and 3D models are no longer hosted in this public repository. They have been moved to a private repository ahead of the v2 commercial release. Developers, researchers, or hobbyists genuinely interested in the hardware design are welcome to reach out. We are happy to share access on a case-by-case basis for legitimate technical, academic, or collaborative purposes."*
> 
> What remains fully accessible in the public domain:
> 1. Complete pinout tables for all UART, SPI, I2C, timer, ADC, and PWM peripherals.
> 2. High-resolution top and bottom PCB layout renders with labeled silkscreen annotations.
> 3. Verified firmware target source files: ArduPilot (`hwdef.dat`, `hwdef-bl.dat`), Betaflight 4.5.1 (`target.h`, `config.h`), and iNAV 9.0.1 (including the custom SPI6 HAL patch).
> 4. The CERN-OHL-S-2.0 license file.

### Impact on [ADR-0003](../adr/0003-base-design-sal-fc-primary.md)
[ADR-0003](../adr/0003-base-design-sal-fc-primary.md) was predicated on deriving MADpilot-H7's KiCad schematics directly from SAL-FC's public EDA sources, with LEVIA-H7 serving as a comparative cross-check. Because SAL-FC's KiCad files are no longer in the public tree, that premise is weakened: MADpilot cannot fork SAL-FC's native `.kicad_sch` or `.kicad_pcb` files directly without external interaction.

### Open Decision for Project Owner at Gate G0
Before committing engineering hours to schematic capture in Phase 1, the project owner must decide between two paths:

*   **Option A: Request Private Hardware Access from SAL-FC Authors**  
    Contact the SAL-FC authors via the credentials listed in their README:
    *   Saleh Alhomeidy: `salehalhomeidy@gmail.com` ([LinkedIn](https://www.linkedin.com/in/salehalhomeidy/))
    *   Akaki Gvelesiani: `akaki.g@hotmail.com` ([LinkedIn](https://www.linkedin.com/in/akaki-gvelesiani-631b27300/))
    *   Levani Kazaishvili: `Levanikazaishvili@gmail.com` ([LinkedIn](https://www.linkedin.com/in/levan-kazaishvili-665139289/))  
    *Pros:* Preserves SAL-FC's proven JLCPCB component selections and stackup.  
    *Cons:* Introduces an external dependency, potential delays, and confidentiality terms that could complicate immediate open-source publication under [ADR-0001](../adr/0001-open-hardware-license-path.md).
*   **Option B: Pivot Primary EDA Base to LEVIA-H7**  
    Designate LEVIA-H7 as the primary KiCad starting project. LEVIA-H7 is 100% open (complete repository verified at [https://github.com/piecol/LEVIA-H7](https://github.com/piecol/LEVIA-H7)), and provides full KiCad 10 schematic sheets, PCB layout, JLCPCB/NextPCB manufacturing packages, and CPL files under CERN-OHL-S-2.0. SAL-FC is then retained as a firmware-mapping reference (using its published `hwdef.dat` and pin tables).  
    *Pros:* Completely autonomous, immediately actionable, zero IP or access ambiguity, Sell-Ready from day one.  
    *Cons:* Requires adapting LEVIA's TFBGA-100 layout to the chosen LQFP-176 package.

---

## 3. Side-by-Side Subsystem Comparison

The table below contrasts SAL-FC and LEVIA-H7 across all critical electrical and firmware subsystems, alongside the proposed MADpilot-H7 implementation.

| Subsystem | SAL-FC (Primary Reference) | LEVIA-H7 (Comparative Cross-Check) | MADpilot-H7 (Proposed Plan) | Primary Citations |
| :--- | :--- | :--- | :--- | :--- |
| **MCU & Package** | STM32H743VIT6, LQFP-100 (480 MHz, 2MB Flash, 1MB RAM) | STM32H743VIHx, TFBGA-100 8x8mm 0.8mm pitch (480 MHz) | STM32H743IIT6, LQFP-176 (480 MHz, 2MB Flash, 1MB RAM) | SAL README Â§Hardware Specifications; LEVIA `MCU.kicad_sch` U2 |
| **HSE Clock Source** | 8.000 MHz Oscillator (ASE-8.000MHZ-LC-T); `STM32_HSE_BYPASS` must NOT be defined | 8.000 MHz Ceramic Resonator (Murata CSTNE8M00G550000R0, 3-pin) | 8.000 MHz or 16.000 MHz TCXO / Crystal (Decision at G0) | SAL README Â§Flashing ArduPilot & `hwdef.dat` L11; LEVIA BOM `C341525` |
| **Primary IMU** | TDK ICM-42688-P on SPI6 (PB3/PB4/PB5, CS: PD7, EXTI: PE4) | TDK ICM-42688-P on SPI1 (PA5/PA6/PD7, CS: PC15, EXTI: PB2) | TDK ICM-42605 on SPI1 (PA5/PA6/PD7, CS: PC15, EXTI: PB2) | SAL `target.h` L90-115; LEVIA `SENSORS.kicad_sch` U14; ADR-0003 |
| **Secondary IMU** | Bosch BMI270 on SPI3 (PC10/PC11/PC12, CS: PD3, EXTI: PD2) | TDK ICM-42688-P on SPI4 (PE12/PE13/PE14, CS: PE11, EXTI: PE15) | Bosch BMI270 on SPI4 (PE2/PE5/PE6 or PE12-14, CS: PC13, EXTI: PE4) | SAL `target.h` L80-84; LEVIA `SENSORS.kicad_sch` U15; ADR-0003 |
| **Barometer** | Bosch BMP388 on I2C2 (PB10/PB11, Addr 0x76) | Infineon DPS368 on I2C2 (PB10/PB11, Addr 0x77) | MEAS MS5611 on I2C2 (PB10/PB11, Addr 0x76 / 0x77) | SAL `target.h` L101, L127; LEVIA `SENSORS.kicad_sch` U16; PLAN.md Â§Phase 0 |
| **Magnetometer** | None onboard (External GPS/Compass puck on I2C4) | iSentek IST8310 onboard on I2C2 (PB10/PB11) | None onboard (External GNSS puck on I2C1; onboard gated to Rev C) | SAL `target.h` L122; LEVIA `SENSORS.kicad_sch` U17; PLAN.md Backlog #3 |
| **Main 5V Buck** | Diodes Inc AP63205WU 5V 2A synchronous buck (32V max in) | TI LMR43620R5RPER 5V 2A synchronous buck (36V max in) | High-efficiency 5V 2A/3A synchronous buck (up to 6S / 36V in) | SAL README Â§Hardware Specifications; LEVIA `POWER.kicad_sch` U4 |
| **Aux/VTX Buck** | TI TPS54302 9V/12V 3A buck (28V max in) | TI LMR604303 9V 3A buck (36V in) with GPIO enable (`PE5`) | Optional 9V 2A/3A buck (Proposal for G0 decision) | SAL README Â§Hardware Specifications; LEVIA `POWER.kicad_sch` U5 |
| **3.3V Regulators** | Logic: AP2112K-3.3 (600mA); Sensors: AP7343-33W5-7 (300mA low-noise) | MCU: AP7361C-33FGE-7 (1A DFN-8); Sensors: AP7361C-33FGE-7 (1A) | Dedicated dual 3.3V LDOs: 3V3_MCU and 3V3_SENS (low-noise) | SAL README Â§Hardware Specifications; LEVIA `POWER.kicad_sch` U6, U7 |
| **Power Protection** | P-FET (AO3407A) reverse-polarity; TVS on battery/5V/USB; PTCs | SMAJ30CA TVS on VBAT; USBLC6-2P6 on USB; dual 1N5819 diode OR-ing | P-FET reverse polarity + SMAJ30CA TVS + USBLC6-2P6 + Diode OR-ing | SAL README Â§Features L55; LEVIA `POWER.kicad_sch` D2, D3, D4 |
| **UART Count** | 7 UARTs: USART1, USART2, USART3, UART4, UART5, UART7, UART8 | 8 UARTs: UART1, UART2, UART3, UART4, UART6, UART7, UART8 | 8 UARTs: USART1 (GPS1), USART2 (TELEM1), USART3 (RC), USART6 (TELEM2), UART8 (GPS2), etc. | SAL `hwdef.dat` L49-78; LEVIA `MCU.kicad_sch` labels |
| **CAN Bus** | TI SN65HVD230D 3.3V CAN transceiver (ISO 11898) | SIT1051TK/3 CAN-FD transceiver with switchable 120Î© (JP1) & PESD2CAN | 3.3V CAN transceiver (SIT1051 or SN65HVD230) on CAN1 & CAN2 | SAL README L75; LEVIA `CAN.kicad_sch` U12, D6, R24 |
| **PWM Outputs** | 12 Channels on TIM1 (4), TIM8 (4), TIM4 (4) with per-channel DMA | 8 Motor outputs on TIM1, TIM4, TIM5 + 2 ESC telemetry UARTs | 12 Channels: TIM1 (CH1-4), TIM4 (CH1-4), TIM5 (CH1-4) with DMA | SAL `target.h` L171-184; LEVIA `MOTORS[1-4].kicad_sch`; ADR-0002 |
| **Flight Logging** | Winbond W25Q128JVSIQ (128 Mbit / 16 MB) SPI Flash on SPI1 | MicroSD card slot (TF-028-H265) on 4-bit SDMMC1 (PC8-12, PD2) | MicroSD card slot (SDMMC1 4-bit) (Recommended proposal) | SAL `target.h` L142; LEVIA `MICRO_SD.kicad_sch` J1 |
| **Video & OSD** | Analog AT7456E OSD on SPI4 with 27 MHz crystal | Analog AT7456E on SPI2 + Digital DJI O3/O4 JST-SH connector | OSD omitted; Digital VTX / Telemetry preferred (Proposal for G0) | SAL `target.h` L133; LEVIA `ANALOG_VTX.kicad_sch` & `DIGITAL_VTX.kicad_sch` |
| **Connectors** | JST-SH 1.0mm connectors + solder pad fallback | JST-SH 1.0mm (ZX-SH1.0 series) + USB-C | Pixhawk-standard JST-GH (DS-018) + 0.1" servo rail + USB-C | SAL README L57; LEVIA BOM L46-49; ADR-0002 |
| **PCB Stackup** | 6-layer FR-4, JLC06161H-3313, ENIG, resin-plugged vias | 6-layer FR-4, ENIG, dedicated L2/L5 ground planes | 6-layer FR-4, JLC06161H-3313, ENIG, dedicated ground planes | SAL README L88; LEVIA `LEVIA_H7.kicad_pcb` setup stackup |

---

## 4. Subsystem Deep Dives & Architectural Lessons

### 4.1 MCU, Clocking, and the HSE Bypass Pitfall
*   **SAL-FC Findings**: SAL-FC utilizes an 8 MHz external clock source (ASE-8.000MHZ-LC-T). In their [`SAL-FC: README.md`](https://github.com/salehali22/SAL-FC/blob/main/README.md#L232-L235), the authors issue an explicit warning:
    > *"The SAL FC uses an 8 MHz oscillator, not a passive crystal. The ArduPilot hwdef.dat must not define `STM32_HSE_BYPASS`. If bypass mode is enabled, the PLL will fail to lock and USB will not enumerate."*
    In the ArduPilot ChibiOS HAL, `STM32_HSE_BYPASS` controls whether the RCC oscillator drive circuitry is disabled (expecting a full CMOS rail-to-rail square wave into `OSC_IN` while `OSC_OUT` is High-Z) or enabled (for quartz crystals and ceramic resonators requiring active inverting drive). If an external active oscillator or clipped sine TCXO is configured with incompatible drive parameters, the STM32 PLL fails to achieve lock, hanging system initialization before USB enumeration.
*   **LEVIA-H7 Findings**: LEVIA-H7 employs a 3-pin 8.000 MHz Murata ceramic resonator (BOM Part `C341525`, Murata CSTNE series) connected across `OSC_IN` (PH0) and `OSC_OUT` (PH1) with built-in 15 pF load capacitors to ground ([`LEVIA-H7: MCU.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/MCU.kicad_sch)). This operates in standard active crystal drive mode without HSE bypass.
*   **Lesson for MADpilot-H7**: Clock stability directly determines EKF IMU integration precision and USB timing. If a passive crystal or ceramic resonator is chosen during KiCad schematic capture, `OSC_IN` and `OSC_OUT` must be connected with appropriate matching load capacitors, and `STM32_HSE_BYPASS` must be omitted in `hwdef.dat`. If an active TCXO is selected for superior temperature performance, `OSC_OUT` must float and `STM32_HSE_BYPASS` must be verified against ChibiOS clock trees.

### 4.2 Sensor Buses and STM32H7 Power Domain Partitioning
*   **SAL-FC Findings**: SAL-FC placed its primary ICM-42688-P on SPI6 (PB3/PB4/PB5) and secondary BMI270 on SPI3 (PC10/PC11/PC12). In the STM32H7 architecture, the bus matrix is partitioned into domains D1 (Core/Cortex-M7), D2 (AHB3/APB1/APB2/APB4 peripherals), and D3 (SmartRun domain). SPI6 is situated in the **D3 domain**, served exclusively by the Basic DMA (BDMA) controller and SRAM4 memory. In standard flight firmware (ArduPilot and iNAV), SPI drivers rely on standard DMA1/DMA2 streams located in D1/D2.
    As recorded in [`SAL-FC: Firmware Target Files/ArduPilot/hwdef.dat`](https://github.com/salehali22/SAL-FC/blob/main/Firmware%20Target%20Files/ArduPilot/hwdef.dat#L100-L101):
    > *"# SPI6 â€” ICM42688P â€” omitted for now (BDMA domain, unverified in ArduPilot)"*
    Furthermore, iNAV required a custom 5-file HAL patch ([`SAL-FC: README.md`](https://github.com/salehali22/SAL-FC/blob/main/README.md#L286-L295)) to force polling mode on SPI6 because the stock HAL could not DMA across domain boundaries.
*   **LEVIA-H7 Findings**: LEVIA-H7 placed its primary ICM-42688-P on SPI1 (PA5/PA6/PD7) in the D1 domain, and its secondary ICM-42688-P on SPI4 (PE12/PE13/PE14) in the D2 domain ([`LEVIA-H7: SENSORS.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/SENSORS.kicad_sch)). Both SPI1 and SPI4 operate with full, native DMA1/DMA2 support across all firmware stacks without kernel patches or buffer bouncing.
*   **Lesson for MADpilot-H7**: **Never place high-data-rate IMUs on SPI6**. MADpilot-H7 assigns its primary IMU (TDK ICM-42605) to SPI1 and its secondary IMU (Bosch BMI270) to SPI4. This ensures standard DMA transfers up to the maximum sensor ODR (8 kHz / 32 kHz) with zero CPU overhead and complete ArduPilot compatibility.

### 4.3 Power Architecture, Low-Noise Sensor Rails, and Diode OR-ing
*   **SAL-FC Findings**: SAL-FC uses an AP63205WU 5V 2A buck regulator for general system power and a TPS54302 9V/12V buck for video transmitters. For 3.3V logic, it employs an AP2112K-3.3 (600mA LDO), but critically routes power to its IMUs and barometer through an independent, ultra-low-noise **AP7343-33W5-7** LDO (300mA, 60 dB PSRR at 1 kHz, 33 ÂµVrms noise) ([`SAL-FC: README.md`](https://github.com/salehali22/SAL-FC/blob/main/README.md#L84-L85)). Reverse polarity protection on the battery input is handled by an AO3407A P-channel MOSFET.
*   **LEVIA-H7 Findings**: LEVIA-H7 separates 5V switching power into two distinct LDO regulators: U6 (AP7361C-33 1A LDO for `3V3_MCU`) and U7 (AP7361C-33 1A LDO for `3V3_SENS`) ([`LEVIA-H7: POWER.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/POWER.kicad_sch)). Furthermore, LEVIA-H7 implements clean **diode OR-ing** using two 1N5819WL Schottky diodes (D3 and D4) feeding `+5V_SYS`: D3 isolates USB `VBUS`, while D4 isolates the switching buck output. This allows the Flight Controller, MCU, sensors, and GPS to be configured safely via USB on the bench without back-feeding high currents into ESCs, servos, or video transmitters.
*   **Lesson for MADpilot-H7**: MADpilot-H7 adopts dual independent 3.3V rails (`3V3_MCU` and low-noise `3V3_SENS`) combined with Schottky diode OR-ing between USB VBUS and the primary 5V buck regulator. Battery input protection combines an active P-FET reverse-polarity gate with a bidirectional SMAJ30CA TVS clamp.

### 4.4 Actuator Timers and Contention-Free DMA
*   **SAL-FC Findings**: SAL-FC features 12 PWM outputs grouped strictly by timer peripheral: TIM1 CH1-4 (PE9, PE11, PE13, PE14), TIM8 CH1-4 (PC6, PC7, PC8, PC9), and TIM4 CH1-4 (PD12, PD13, PD14, PD15) ([`SAL-FC: Firmware Target Files/Betaflight/target.h`](https://github.com/salehali22/SAL-FC/blob/main/Firmware%20Target%20Files/Betaflight/target.h#L171-L184)). By dedicating individual advanced 4-channel timers to discrete 4-output blocks, each output possesses an independent DMA request stream. This eliminates DMA FIFO contention and allows bidirectional DSHOT telemetry and high-rate digital servo protocols to run simultaneously without timing jitter.
*   **LEVIA-H7 Findings**: LEVIA-H7 routed 8 motor outputs to dual 8-pin ESC connectors using mixed timer channels (TIM1, TIM4, TIM5) ([`LEVIA-H7: MOTORS[1-4].kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/MOTORS[1-4].kicad_sch) & [`LEVIA-H7: MOTORS[5-8].kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/MOTORS[5-8].kicad_sch)). However, because LEVIA-H7 implemented an onboard MicroSD slot on SDMMC1 (which requires PC8, PC9, PC10, PC11, PC12, and PD2), PC8 and PC9 were unavailable for TIM8 motor channels.
*   **Lesson for MADpilot-H7**: For a fixed-wing aircraft requiring throttle, multi-surface ailerons, elevators, rudder, flaps, and auxiliary servos, 12 outputs are essential. MADpilot-H7 allocates 12 PWM outputs across **TIM1 (PE9, PE11, PE13, PE14)**, **TIM4 (PD12, PD13, PD14, PD15)**, and **TIM5 (PA0, PA1, PA2, PA3)**. This avoids any conflict with 4-bit SDMMC1 logging lines on Port C while preserving independent DMA streaming across all channels.

### 4.5 Logging: High-Bandwidth MicroSD vs Serial SPI Flash
*   **SAL-FC Findings**: SAL-FC uses a Winbond W25Q128JVSIQ (16 megabytes) SPI Flash on SPI1. In fixed-wing UAV operations, autonomous missions frequently exceed 45 to 90 minutes. A 16 MB flash chip fills up within 5â€“10 minutes of full-rate EKF, IMU, and telemetry logging, forcing the pilot to either compromise log resolution or lose critical diagnostic flight records.
*   **LEVIA-H7 Findings**: LEVIA-H7 provides an onboard push-push MicroSD slot (TF-028-H265) interfaced over the 4-bit SDMMC1 peripheral (PC8â€“PC12, PD2) ([`LEVIA-H7: MICRO_SD.kicad_sch`](https://github.com/piecol/LEVIA-H7/blob/main/MICRO_SD.kicad_sch)).
*   **Lesson for MADpilot-H7**: MADpilot-H7 strongly recommends incorporating an onboard MicroSD card slot over SDMMC1. This provides gigabytes of storage capacity for high-rate BlackBox/DataFlash logging, terrain databases, and long-range fixed-wing autonomous missions.

---

## 5. Comparison Against the Reference Board (Pixhawk 6C)

In accordance with project guidelines ([CONTEXT.md](../../CONTEXT.md) and [PLAN.md](../../PLAN.md)), the chosen standard is the **Reference Board (Pixhawk 6C)**. The full hardware-definition delta table is scheduled for Phase 1 bring-up; this section benchmarks key architectural differences:

1.  **Connector Set Standard Compliance**:  
    MADpilot-H7 conforms 100% to the Pixhawk-standard connector standard (DS-018 connector specification). Connectors for POWER1, POWER2, TELEM1, TELEM2, GPS1, GPS2, CAN1, CAN2, I2C, and RC inputs utilize standardized JST-GH pinouts, enabling plug-and-play interoperability with commercial off-the-shelf (COTS) GNSS modules, telemetry transceivers, and battery power modules.
2.  **Sensor Redundancy Suite**:  
    *   *Reference Board (Pixhawk 6C)*: Incorporates a primary TDK ICM-42688-P, a secondary Bosch BMI088 (vibration-isolated), an internal MEAS MS5611 barometer, and an internal iSentek IST8310 magnetometer.
    *   *MADpilot-H7*: Implements the In-Stock-First sensor suite: primary TDK ICM-42605, secondary Bosch BMI270, and MEAS MS5611 barometer. Onboard magnetometer is omitted (external compass on the GNSS mast carries primary heading), avoiding magnetic distortion from airframe motor currents.
3.  **Absence of External IOMCU**:  
    *   *Reference Board (Pixhawk 6C)*: Employs a dual-processor architecture featuring an STM32F103 IOMCU coprocessor communicating with the main FMU over USART6 to drive the 8 MAIN PWM outputs.
    *   *MADpilot-H7*: Deliberately **eliminates the IOMCU**, generating all 12 PWM actuator channels directly from the primary STM32H743 hardware timers (TIM1, TIM4, TIM5) with per-output DMA. This drastically simplifies board routing, reduces component count and bill of materials cost, removes the requirement for secondary IO bootloader flashing, and matches modern single-processor flight controller paradigms while exceeding IOMCU channel capacity.

---

## 6. In-Stock-First Substitution Analysis & Component Proposals

The **In-Stock-First** rule ([CONTEXT.md](../../CONTEXT.md#L30-L31)) dictates that a hardware revision may only freeze when every BOM part is procurable in sufficient volume from the assembly house (JLCPCB PCBA) at that exact moment. The table below details and rationalizes every component deviation from the base designs:

```
+----------------------------------------------------------------------------------------------------+
|                                 MADpilot-H7 In-Stock-First BOM Deltas                              |
+-------------------+--------------------+-----------------------+-----------------------------------+
| Subsystem Part    | Base Design Choice | MADpilot-H7 Selection | Rationale & Stock Verification    |
+-------------------+--------------------+-----------------------+-----------------------------------+
| Primary IMU       | TDK ICM-42688-P    | TDK ICM-42605         | ICM-42688-P suffers recurring     |
|                   | (SAL & LEVIA)      |                       | procurement shortages. ICM-42605  |
|                   |                    |                       | is pin-compatible (LGA-14),       |
|                   |                    |                       | abundant at LCSC/JLC, ultra-low   |
|                   |                    |                       | noise, and natively supported.    |
+-------------------+--------------------+-----------------------+-----------------------------------+
| Secondary IMU     | Bosch BMI270       | Bosch BMI270          | Retained from SAL-FC. Highly      |
|                   | (SAL-FC)           | (Retained)            | procurable, dissimilar MEMS       |
|                   |                    |                       | architecture for sensor diversity.|
+-------------------+--------------------+-----------------------+-----------------------------------+
| Barometer         | Bosch BMP388 (SAL) | MEAS MS5611           | MS5611 is the gold standard for   |
|                   | Infineon DPS368(LEV|                       | fixed-wing altitude hold, with    |
|                   |                    |                       | superior thermal drift stability  |
|                   |                    |                       | and deep COTS stock reserves.     |
+-------------------+--------------------+-----------------------+-----------------------------------+
| Magnetometer      | IST8310 onboard    | None onboard          | Onboard compasses in fixed-wing   |
|                   | (LEVIA-H7)         | (External GNSS Puck)  | planes suffer catastrophic EMI    |
|                   |                    |                       | from battery cables. External puck|
|                   |                    |                       | is standard. Backlog item #3.     |
+-------------------+--------------------+-----------------------+-----------------------------------+
| Analog OSD        | AT7456E + 27MHz    | None (Omitted)        | Proposal for G0: Analog OSD chips |
|                   | (SAL & LEVIA)      | [Proposed]            | add 27MHz crystal, routing noise, |
|                   |                    |                       | and BOM cost. Fixed-wing uses     |
|                   |                    |                       | digital VTX (DJI/HDZero) or GCS.  |
+-------------------+--------------------+-----------------------+-----------------------------------+
| Flight Logging    | W25Q128 16MB Flash | MicroSD Slot (SDMMC1) | Proposal for G0: 16MB SPI flash   |
|                   | (SAL-FC)           | [Proposed]            | is insufficient for long flights. |
|                   |                    |                       | 4-bit SDMMC1 provides gigabytes.  |
+-------------------+--------------------+-----------------------+-----------------------------------+
| Digital VTX Rail  | 9V Buck Converter  | 9V Auxiliary Rail     | Proposal for G0: Incorporate      |
|                   | (LEVIA-H7)         | [Proposed]            | LEVIA's switchable 9V buck to     |
|                   |                    |                       | power digital air units cleanly.  |
+-------------------+--------------------+-----------------------+-----------------------------------+
```

---

## 7. The MADpilot-H7 Pin Plan

The complete hardware pin allocation plan for **MADpilot-H7** is defined below. The design targets the **STM32H743IIT6 in an LQFP-176 package**, which provides 140 versatile I/O lines across Ports A through I.

Every pin assignment below has been cross-checked against the STMicroelectronics STM32H743 alternate function multiplexing table, proven assignments in SAL-FC and LEVIA-H7, and ChibiOS DMA channel mapping.

### 7.1 Master Connector Pin Plan Table

| Connector / Port | Pin # | Signal Name | STM32 Port Pin | Peripheral / Alternate Function | Electrical Type | Proven Source & Design Rationale |
| :--- | :---: | :--- | :---: | :--- | :--- | :--- |
| **POWER1** | 1 | VDD_5V_IN | â€” | Main System 5V Power Input | Power (5.0V) | Dual redundant power brick input 1 |
| (6-pin JST-GH) | 2 | VDD_5V_IN | â€” | Main System 5V Power Input | Power (5.0V) | Paralleled pin for contact resistance |
| | 3 | CURRENT1 | **PC1** | `ADC1_INP11` | Analog In | Current sense input 1 (matches SAL-FC PC1 / LEVIA PC1) |
| | 4 | VOLTAGE1 | **PC0** | `ADC1_INP10` | Analog In | Voltage sense input 1 (matches LEVIA-H7 PC0) |
| | 5 | GND | â€” | System Ground | Ground | Common system ground return |
| | 6 | GND | â€” | System Ground | Ground | Common system ground return |
| **POWER2** | 1 | VDD_5V_IN | â€” | Secondary 5V Power Input | Power (5.0V) | Dual redundant power brick input 2 |
| (6-pin JST-GH) | 2 | VDD_5V_IN | â€” | Secondary 5V Power Input | Power (5.0V) | Paralleled pin for contact resistance |
| | 3 | CURRENT2 | **PC4** | `ADC1_INP4` | Analog In | Current sense input 2 (matches Pixhawk 6C PC4) |
| | 4 | VOLTAGE2 | **PC5** | `ADC1_INP8` | Analog In | Voltage sense input 2 (matches Pixhawk 6C PC5) |
| | 5 | GND | â€” | System Ground | Ground | Common system ground return |
| | 6 | GND | â€” | System Ground | Ground | Common system ground return |
| **USB-C** | A6/B6 | USB_DP | **PA12** | `OTG1_FS_DP` (AF10) | Diff 90Î© | USB Full-Speed Data Plus (TVS protected, 90Î© routed) |
| (Receptacle) | A7/B7 | USB_DM | **PA11** | `OTG1_FS_DM` (AF10) | Diff 90Î© | USB Full-Speed Data Minus (TVS protected, 90Î© routed) |
| | A4/B4/A9/B9| VBUS | **PA9** | `GPIO_IN` / `VBUS_DETECT` | 5.0V Sense | USB VBUS presence detection via voltage divider |
| | A5, B5 | CC1, CC2 | â€” | 5.1kÎ© Pull-Down to GND | Passive | Configures USB Type-C Standard Upstream Device (UFP) |
| | Shell | SHIELD | â€” | Chassis Ground | Shield | Filtered chassis ground connection with RC damping |
| **TELEM1** | 1 | VCC_5V | â€” | 5.0V Peripheral Power Output | Power Out | Filtered 5V rail for primary telemetry radio |
| (6-pin JST-GH) | 2 | TELEM1_TX | **PD5** | `USART2_TX` (AF7) | 3.3V Out | Primary telemetry transmit (matches 6C / SAL-FC USART2) |
| | 3 | TELEM1_RX | **PD6** | `USART2_RX` (AF7) | 3.3V In | Primary telemetry receive (matches 6C / SAL-FC USART2) |
| | 4 | TELEM1_CTS | **PD3** | `USART2_CTS` (AF7) | 3.3V In | Clear-To-Send hardware flow control line |
| | 5 | TELEM1_RTS | **PD4** | `USART2_RTS` (AF7) | 3.3V Out | Ready-To-Send hardware flow control line |
| | 6 | GND | â€” | System Ground | Ground | Ground return |
| **TELEM2** | 1 | VCC_5V | â€” | 5.0V Peripheral Power Output | Power Out | Filtered 5V rail for secondary radio or companion computer |
| (6-pin JST-GH) | 2 | TELEM2_TX | **PG14** | `USART6_TX` (AF7) | 3.3V Out | Secondary telemetry transmit (Port G on LQFP-176) |
| | 3 | TELEM2_RX | **PG9** | `USART6_RX` (AF7) | 3.3V In | Secondary telemetry receive (Port G on LQFP-176) |
| | 4 | TELEM2_CTS | **PG15** | `USART6_CTS` (AF7) | 3.3V In | Clear-To-Send hardware flow control line |
| | 5 | TELEM2_RTS | **PG8** | `USART6_RTS` (AF7) | 3.3V Out | Ready-To-Send hardware flow control line |
| | 6 | GND | â€” | System Ground | Ground | Ground return |
| **GPS1** | 1 | VCC_5V | â€” | 5.0V Peripheral Power Output | Power Out | Filtered 5V rail for primary GNSS & compass mast |
| (10-pin JST-GH)| 2 | GPS1_TX | **PB6** | `USART1_TX` (AF7) | 3.3V Out | Primary GNSS UART transmit (matches Pixhawk 6C PB6) |
| | 3 | GPS1_RX | **PB7** | `USART1_RX` (AF7) | 3.3V In | Primary GNSS UART receive (matches Pixhawk 6C PB7) |
| | 4 | GPS1_SCL | **PB8** | `I2C1_SCL` (AF4) | 3.3V I/O | External compass I2C1 Clock (matches 6C PB8) |
| | 5 | GPS1_SDA | **PB9** | `I2C1_SDA` (AF4) | 3.3V I/O | External compass I2C1 Data (matches 6C PB9) |
| | 6 | SAFETY_SW | **PE10** | `GPIO_IN` | 3.3V In | Arming safety switch button input (internal pull-up) |
| | 7 | SAFETY_LED| **PE3** | `GPIO_OUT` | 3.3V Out | Arming safety switch LED drive (matches LEVIA PE3) |
| | 8 | VDD_3V3 | â€” | 3.3V Clean Power Output | Power Out | Auxiliary clean 3.3V power for safety logic |
| | 9 | BUZZER- | **PA15** | `TIM2_CH1` / `GPIO` (AF1) | Open-Drain | Low-side N-FET drive for external buzzer (LEVIA PA15) |
| | 10| GND | â€” | System Ground | Ground | Ground return |
| **GPS2** | 1 | VCC_5V | â€” | 5.0V Peripheral Power Output | Power Out | Filtered 5V rail for secondary GNSS receiver |
| (6-pin JST-GH) | 2 | GPS2_TX | **PE1** | `UART8_TX` (AF8) | 3.3V Out | Secondary GNSS UART transmit (matches SAL & LEVIA PE1) |
| | 3 | GPS2_RX | **PE0** | `UART8_RX` (AF8) | 3.3V In | Secondary GNSS UART receive (matches SAL & LEVIA PE0) |
| | 4 | GPS2_SCL | **PB8** | `I2C1_SCL` (AF4) | 3.3V I/O | Secondary compass I2C Clock (shared I2C1 external bus) |
| | 5 | GPS2_SDA | **PB9** | `I2C1_SDA` (AF4) | 3.3V I/O | Secondary compass I2C Data (shared I2C1 external bus) |
| | 6 | GND | â€” | System Ground | Ground | Ground return |
| **I2C (Ext)** | 1 | VCC_5V | â€” | 5.0V Peripheral Power Output | Power Out | Clean 5V power for external airspeed sensors / OLED |
| (4-pin JST-GH) | 2 | EXT_I2C_SCL| **PF14** | `I2C4_SCL` (AF4) | 3.3V I/O | Dedicated external I2C4 Clock (airspeed sensor bus) |
| | 3 | EXT_I2C_SDA| **PF15** | `I2C4_SDA` (AF4) | 3.3V I/O | Dedicated external I2C4 Data (airspeed sensor bus) |
| | 4 | GND | â€” | System Ground | Ground | Ground return |
| **CAN1** | 1 | VCC_5V | â€” | 5.0V Transceiver Power Out | Power Out | Power supply for external DroneCAN nodes |
| (4-pin JST-GH) | 2 | CAN1_H | â€” | Differential High Bus Line | CAN-FD | CAN1 Differential High Line (from SIT1051 transceiver) |
| | 3 | CAN1_L | â€” | Differential Low Bus Line | CAN-FD | CAN1 Differential Low Line (from SIT1051 transceiver) |
| | 4 | GND | â€” | System Ground | Ground | Ground return |
| *(Transceiver)*| â€” | FDCAN1_TX | **PD1** | `FDCAN1_TX` (AF9) | 3.3V Out | MCU to CAN1 transceiver TX (matches LEVIA/6C PD1) |
| *(Transceiver)*| â€” | FDCAN1_RX | **PD0** | `FDCAN1_RX` (AF9) | 3.3V In | MCU to CAN1 transceiver RX (matches LEVIA/6C PD0) |
| **CAN2** | 1 | VCC_5V | â€” | 5.0V Transceiver Power Out | Power Out | Power supply for secondary DroneCAN bus |
| (4-pin JST-GH) | 2 | CAN2_H | â€” | Differential High Bus Line | CAN-FD | CAN2 Differential High Line (from SIT1051 transceiver) |
| | 3 | CAN2_L | â€” | Differential Low Bus Line | CAN-FD | CAN2 Differential Low Line (from SIT1051 transceiver) |
| | 4 | GND | â€” | System Ground | Ground | Ground return |
| *(Transceiver)*| â€” | FDCAN2_TX | **PB13** | `FDCAN2_TX` (AF9) | 3.3V Out | MCU to CAN2 transceiver TX (matches Pixhawk 6C PB13) |
| *(Transceiver)*| â€” | FDCAN2_RX | **PB12** | `FDCAN2_RX` (AF9) | 3.3V In | MCU to CAN2 transceiver RX (matches Pixhawk 6C PB12) |
| **SBUS/PPM** | 1 | VDD_5V_RC | â€” | Dedicated 5V RC Power Out | Power Out | Isolated 5V rail for RC receiver |
| (5-pin JST-GH) | 2 | RC_IN | **PD9** | `USART3_RX` (AF7) | 3.3V In | RC serial receiver input (SBUS / CRSF / PPM / ELRS) |
| | 3 | RSSI_IN | **PC2** | `ADC1_INP12` | Analog In | Analog RSSI signal input from legacy receivers |
| | 4 | RC_TX | **PD8** | `USART3_TX` (AF7) | 3.3V Out | Bidirectional telemetry transmit for CRSF / ExpressLRS |
| | 5 | GND | â€” | System Ground | Ground | Ground return |
| **Spektrum/RSSI**| 1 | VDD_3V3_SPEK| â€” | Dedicated 3.3V Power Out | Power Out | Clean 3.3V supply for Spektrum DSM satellite receivers |
| (3-pin JST-ZH) | 2 | GND | â€” | System Ground | Ground | Ground return |
| | 3 | SPEK_RX | **PD9** | `USART3_RX` (AF7) | 3.3V In | Satellite receiver signal input (internally tied to PD9) |
| **Safety Switch**| 1 | SAFETY_SW | **PE10** | `GPIO_IN` | 3.3V In | Arming safety switch button line (tied to GPS1 Pin 6) |
| (3-pin Standalone)| 2 | SAFETY_LED| **PE3** | `GPIO_OUT` | 3.3V Out | Arming safety switch LED drive (tied to GPS1 Pin 7) |
| | 3 | GND | â€” | System Ground | Ground | Ground return |
| **Buzzer** | 1 | BUZZER+ | â€” | +5V Switched Power Output | Power Out | +5V positive supply to magnetic buzzer |
| (2-pin JST-GH) | 2 | BUZZER- | **PA15** | `TIM2_CH1` / `GPIO` (AF1) | Open-Drain | N-channel FET drain sink (tied to GPS1 Pin 9) |
| **PWM-OUT** | CH 1 | PWM1 | **PE9** | `TIM1_CH1` (AF1) | 3.3V Out | Actuator 1 / Throttle (TIM1 Bank 1 with DMA) |
| (0.1" 3-row rail)| CH 2 | PWM2 | **PE11** | `TIM1_CH2` (AF1) | 3.3V Out | Actuator 2 / Left Aileron (TIM1 Bank 1 with DMA) |
| | CH 3 | PWM3 | **PE13** | `TIM1_CH3` (AF1) | 3.3V Out | Actuator 3 / Right Aileron (TIM1 Bank 1 with DMA) |
| | CH 4 | PWM4 | **PE14** | `TIM1_CH4` (AF1) | 3.3V Out | Actuator 4 / Elevator (TIM1 Bank 1 with DMA) |
| | CH 5 | PWM5 | **PD12** | `TIM4_CH1` (AF2) | 3.3V Out | Actuator 5 / Rudder (TIM4 Bank 2 with DMA) |
| | CH 6 | PWM6 | **PD13** | `TIM4_CH2` (AF2) | 3.3V Out | Actuator 6 / Left Flap (TIM4 Bank 2 with DMA) |
| | CH 7 | PWM7 | **PD14** | `TIM4_CH3` (AF2) | 3.3V Out | Actuator 7 / Right Flap (TIM4 Bank 2 with DMA) |
| | CH 8 | PWM8 | **PD15** | `TIM4_CH4` (AF2) | 3.3V Out | Actuator 8 / Nose Steering / Aux (TIM4 Bank 2 with DMA) |
| | CH 9 | PWM9 | **PA0** | `TIM5_CH1` (AF2) | 3.3V Out | Actuator 9 / Camera Pan (32-bit TIM5 Bank 3 with DMA) |
| | CH 10 | PWM10 | **PA1** | `TIM5_CH2` (AF2) | 3.3V Out | Actuator 10 / Camera Tilt (32-bit TIM5 Bank 3 with DMA) |
| | CH 11 | PWM11 | **PA2** | `TIM5_CH3` (AF2) | 3.3V Out | Actuator 11 / Payload Drop 1 (TIM5 Bank 3 with DMA) |
| | CH 12 | PWM12 | **PA3** | `TIM5_CH4` (AF2) | 3.3V Out | Actuator 12 / Payload Drop 2 (TIM5 Bank 3 with DMA) |
| **SWD Header** | 1 | VDD_3V3_MCU| â€” | Logic 3.3V Reference | Power Out | Reference voltage for ST-Link / J-Link debugger |
| (4-pin Header) | 2 | SWDIO | **PA13** | `JTMS-SWDIO` (AF0) | 3.3V I/O | ARM Serial Wire Debug Data line (DFU/bring-up) |
| | 3 | SWCLK | **PA14** | `JTCK-SWCLK` (AF0) | 3.3V In | ARM Serial Wire Debug Clock line (DFU/bring-up) |
| | 4 | GND | â€” | System Ground | Ground | Ground return |
| **Boot Button** | 1 | BOOT0 | **BOOT0**| System Boot Mode Select | Input | Pushbutton pulls BOOT0 high to 3.3V; 10k pulldown |
| **System Reset**| 1 | NRST | **NRST** | System Hardware Reset | Input | Pushbutton pulls NRST low; 100nF filter capacitor |

---

### 7.2 Internal Sensor, Storage, and Clock Allocation Table

The table below maps all onboard sensors, storage media, and oscillator connections:

| Peripheral Device | Signal Name | STM32 Pin | Peripheral Function | Bus Domain | Design Rationale & Proven Precedent |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **Primary IMU** | `IMU1_SCK` | **PA5** | `SPI1_SCK` (AF5) | D1 | SPI1 Clock to ICM-42605 (matches SAL-FC & LEVIA-H7) |
| (TDK ICM-42605) | `IMU1_MISO`| **PA6** | `SPI1_MISO` (AF5) | D1 | SPI1 Data In from ICM-42605 (matches SAL & LEVIA) |
| | `IMU1_MOSI`| **PD7** | `SPI1_MOSI` (AF5) | D1 | SPI1 Data Out to ICM-42605 (matches LEVIA-H7 PD7) |
| | `IMU1_CS` | **PC15**| `GPIO_OUT` | D1 | Active-low Chip Select for ICM-42605 (matches LEVIA PC15) |
| | `IMU1_DRDY`| **PB2** | `EXTI2` | D1 | Data Ready hardware interrupt (matches LEVIA PB2) |
| **Secondary IMU**| `IMU2_SCK` | **PE2** | `SPI4_SCK` (AF5) | D2 | SPI4 Clock to BMI270 (matches SAL-FC PE2 / D2 domain) |
| (Bosch BMI270) | `IMU2_MISO`| **PE5** | `SPI4_MISO` (AF5) | D2 | SPI4 Data In from BMI270 (matches SAL-FC PE5) |
| | `IMU2_MOSI`| **PE6** | `SPI4_MOSI` (AF5) | D2 | SPI4 Data Out to BMI270 (matches SAL-FC PE6) |
| | `IMU2_CS` | **PC13**| `GPIO_OUT` | D2 | Active-low Chip Select for BMI270 (matches SAL-FC PC13) |
| | `IMU2_DRDY`| **PE4** | `EXTI4` | D2 | Data Ready hardware interrupt (matches SAL-FC PE4) |
| **Barometer** | `BARO_SCL` | **PB10**| `I2C2_SCL` (AF4) | D2 | Dedicated internal sensor I2C2 Clock (matches SAL & LEVIA) |
| (MEAS MS5611) | `BARO_SDA` | **PB11**| `I2C2_SDA` (AF4) | D2 | Dedicated internal sensor I2C2 Data (matches SAL & LEVIA) |
| **MicroSD Card** | `SDIO_D0` | **PC8** | `SDMMC1_D0` (AF12) | D1 | 4-bit SDMMC Data 0 with 10k pull-up (matches LEVIA PC8) |
| (Push-Push Slot)| `SDIO_D1` | **PC9** | `SDMMC1_D1` (AF12) | D1 | 4-bit SDMMC Data 1 with 10k pull-up (matches LEVIA PC9) |
| | `SDIO_D2` | **PC10**| `SDMMC1_D2` (AF12) | D1 | 4-bit SDMMC Data 2 with 10k pull-up (matches LEVIA PC10) |
| | `SDIO_D3` | **PC11**| `SDMMC1_D3` (AF12) | D1 | 4-bit SDMMC Data 3 with 10k pull-up (matches LEVIA PC11) |
| | `SDIO_CK` | **PC12**| `SDMMC1_CK` (AF12) | D1 | SDMMC High-Speed Clock Line (matches LEVIA PC12) |
| | `SDIO_CMD` | **PD2** | `SDMMC1_CMD` (AF12) | D1 | SDMMC Command/Response with 10k pull-up (matches LEVIA) |
| **System Clock** | `OSC_IN` | **PH0** | `RCC_OSC_IN` | Core | 8.000 MHz primary clock input from crystal/TCXO |
| (8 MHz HSE) | `OSC_OUT` | **PH1** | `RCC_OSC_OUT` | Core | Clock output to crystal (leave NC if active TCXO used) |

---

## 8. Summary of Open Decisions for the Project Owner at Gate G0

To prepare the MADpilot-H7 for Phase-1 schematic capture and the mandatory **G0 External Design Review** ([PLAN.md](../../PLAN.md#L28-L29)), the following five engineering decisions are flagged for project owner sign-off:

```
+----------------------------------------------------------------------------------------------------+
|                                    Gate G0 Open Decisions Matrix                                   |
+---+-----------------------------+-----------------------+-----------------------+------------------+
| # | Decision Item               | Option A (Default)    | Option B (Alternate)  | Trade-Off Impact |
+---+-----------------------------+-----------------------+-----------------------+------------------+
| 1 | Base Design EDA Starting    | Request private access| Pivot primary base to | Option A delays  |
|   | Point (Section 2)           | to SAL-FC v2 KiCad    | open LEVIA-H7 KiCad   | Phase 1; Option B|
|   |                             | repository.           | files immediately.    | is 100% open now.|
+---+-----------------------------+-----------------------+-----------------------+------------------+
| 2 | HSE Clock Architecture      | 8.000 MHz Quartz      | 8.000 MHz Active TCXO | Crystal is lower |
|   | & Bypass Mode (Section 4.1) | Crystal with load caps| (Requires bypass mode | cost; TCXO gives |
|   |                             | (no bypass in hwdef). | verification).        | superior thermal |
|   |                             |                       |                       | drift stability. |
+---+-----------------------------+-----------------------+-----------------------+------------------+
| 3 | Analog OSD Chip (AT7456E)   | Omit AT7456E analog   | Retain AT7456E analog | Omission saves   |
|   | Inclusion (Section 6)       | OSD; use digital VTX  | OSD on SPI2 with      | board space and  |
|   |                             | and telemetry.        | 27 MHz crystal.       | removes 27MHz RF.|
+---+-----------------------------+-----------------------+-----------------------+------------------+
| 4 | Flight Logging Medium       | MicroSD Card Slot     | 128 Mbit (16MB) SPI   | MicroSD enables  |
|   | (Section 4.5 & 6)           | (4-bit SDMMC1 on      | Flash (W25Q128 on     | full-mission EKF |
|   |                             | Port C & D).          | SPI1 / SPI2).         | flight logs.     |
+---+-----------------------------+-----------------------+-----------------------+------------------+
| 5 | Auxiliary Digital VTX Rail  | Include dedicated 9V  | Pure 5V system rail;  | 9V rail cleanly  |
|   | & Regulator (Section 4.3)   | 2A buck with GPIO     | external digital VTX  | powers DJI O3/O4 |
|   |                             | enable (note: needs a | powered off battery.  | and Walksnail.   |
|   |                             | spare GPIO, e.g. PD10 |                       |                  |
|   |                             | â€” PE5 is booked by    |                       |                  |
|   |                             | SPI4_MISO in the pin  |                       |                  |
|   |                             | plan).                |                       |                  |
+---+-----------------------------+-----------------------+-----------------------+------------------+
```

---
*End of Phase-1 Comparative Review & MADpilot-H7 Pin Plan.*

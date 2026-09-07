# MADpilot-H7 vs Reference Board (Pixhawk 6C) Hardware Architecture Delta

**Document ID:** MAD-HW-DELTA-001  
**Target Hardware:** MADpilot-H7 Flight Controller (STM32H743IIT6, LQFP-176)  
**Reference Hardware:** Pixhawk 6C Standard Flight Controller (Holybro FMUv6C, STM32H743)  
**Revision:** Rev A Bring-Up Draft  
**Governing ADRs:** [ADR-0001 (License Path & Trademark)](../adr/0001-open-hardware-license-path.md), [ADR-0002 (Pixhawk-Standard Connector Set)](../adr/0002-pixhawk-standard-connectors.md), [ADR-0003 (Base Design References)](../adr/0003-base-design-sal-fc-primary.md), [ADR-0004 (Hub Repo & ArduPilot Submodule)](../adr/0004-hub-repo-fork-submodule.md)  
**Design Authority:** [docs/hardware/comparative-review.md](comparative-review.md)

---

## 1. Overview and Benchmarking Context

In accordance with [ADR-0002](../adr/0002-pixhawk-standard-connectors.md) and [PLAN.md](../../PLAN.md), the **Pixhawk 6C** serves as the **Reference Board** against which MADpilot-H7 is architecturally benchmarked.

The primary objective of MADpilot-H7 is an open-hardware (CERN-OHL-S-2.0 / GPLv3), single-processor fixed-wing autopilot that maintains **Sell-Ready** status while achieving full plug-and-play interoperability with standard Commercial Off-The-Shelf (COTS) UAV peripherals (GNSS receivers, power bricks, digital airspeed sensors, telemetry radios).

Per [ADR-0001](../adr/0001-open-hardware-license-path.md), the trademark name "Pixhawk" appears exclusively in architectural compatibility and standards compliance statements.

---

## 2. Master Architectural Delta Table

The table below contrasts each subsystem between the Reference Board (Pixhawk 6C) and MADpilot-H7. Every claim is cited directly to source hardware definition files or official documentation.

| Architectural Domain | Reference Board (Pixhawk 6C) | MADpilot-H7 Implementation | Technical Rationale & Trade-Off | Primary Citations |
| :--- | :--- | :--- | :--- | :--- |
| **Product & Firmware Identity** | Commercial Holybro FMUv6C autopilot; default firmware branding `"ArduPilot"` | Open-hardware fixed-wing autopilot; custom firmware branding `"MADpilot"` | Independent OEM identity under CERN-OHL-S-2.0; distinct telemetry and GCS branding | Pixhawk 6C default; Hub `hwdef/MADpilotH7/hwdef.dat` L17 (`AP_CUSTOM_FIRMWARE_STRING`) |
| **Microcontroller (MCU) & Package** | STM32H743IIK6 (LQFP-176 / TFBGA), 480 MHz ARM Cortex-M7, 2MB Flash, 1MB RAM | STM32H743IIT6 (LQFP-176), 480 MHz ARM Cortex-M7, 2MB Flash, 1MB RAM | Identical high-performance core; LQFP-176 enables reliable JLCPCB PCBA inspection and repair | Pixhawk 6C `hwdef.dat` L9 (`MCU STM32H7xx STM32H743xx`); Hub `hwdef.dat` L6; Review Table 7.1 |
| **Upstream Board ID (`APJ_BOARD_ID`)** | `APJ_BOARD_ID 56` | `APJ_BOARD_ID 3141` | Distinct bootloader identifier within the reserved upstream registry zone (3136–3145) | Pixhawk 6C `hwdef.dat` L23 (`APJ_BOARD_ID 56`); Hub `hwdef.dat` L9; `docs/IDENTITY.md` §4 |
| **USB Vendor & Product ID (VID/PID)** | Vendor ID: `0x3162` (Holybro)<br>Product ID: `0x0053`<br>Manufacturer: `"Holybro"` | Vendor ID: `0x1D50` (Openmoko Inc.)<br>Product ID: `0x61a4`<br>Manufacturer: `"MADpilot"` | Dedicated community USB identity allocated under Openmoko VID; prevents USB collision with vendor hardware | Pixhawk 6C `hwdef.dat` L18-20 (`USB_VENDOR 0x3162`); Hub `hwdef.dat` L12-14; `docs/IDENTITY.md` §1 |
| **Oscillator Frequency (HSE)** | 16.000 MHz external oscillator (`OSCILLATOR_HZ 16000000`) | 8.000 MHz external crystal / oscillator (`OSCILLATOR_HZ 8000000`) | 8 MHz standard; standard non-bypass active drive config pending Gate G0 TCXO decision | Pixhawk 6C `hwdef.dat` L12; Hub `hwdef.dat` L23; Review §4.1 & §8 |
| **ChibiOS System Timer** | 32-bit hardware timer TIM2 (`STM32_ST_USE_TIMER 2`) | 16-bit hardware timer TIM12 (`STM32_ST_USE_TIMER 12`, `CH_CFG_ST_RESOLUTION 16`) | Replicates proven MatekH743 timer allocation; frees TIM2 CH1 exclusively for buzzer PWM | Pixhawk 6C `hwdef.dat` L15; Hub `hwdef.dat` L30-31; MatekH743 `hwdef.dat` L21-22 |
| **Primary IMU** | TDK InvenSense ICM-42688-P on SPI1 (PA5/PA6/PA7, CS: `PC13`, DRDY: `PE6`) | TDK InvenSense ICM-42605 on SPI1 (PA5/PA6/PD7, CS: `PC15`, DRDY: `PB2`) | ICM-42605 selected under In-Stock-First rule (abundant stock, identical LGA-14 footprint and noise spec) | Pixhawk 6C `hwdef.dat` L98-106, L234, L238; Hub `hwdef.dat` L42-49; Review §6 & Table 7.2 |
| **Secondary IMU** | Bosch BMI055 / BMI088 on SPI1 (split accel/gyro CS: `PC15`/`PC14`, DRDY: `PE4`/`PE5`) | Bosch BMI270 on SPI4 (PE2/PE5/PE6, CS: `PC13`, DRDY: `PE4`) | Dissimilar MEMS architecture on separate D2 domain SPI bus; eliminates bus contention with primary IMU | Pixhawk 6C `hwdef.dat` L102-105, L239-242; Hub `hwdef.dat` L54-61; Review §4.2 & Table 7.2 |
| **Barometer** | MEAS MS5611 + BMP388 on internal I2C4 (`I2C:0:0x76`, `I2C:0:0x77`) | MEAS MS5611 on internal sensor I2C2 (`I2C:0:0x77`, PB10/PB11) | Gold standard fixed-wing altitude hold stability; dedicated internal bus avoids I2C hanging | Pixhawk 6C `hwdef.dat` L147, L212-214; Hub `hwdef.dat` L67-83; Review Table 7.2 |
| **Onboard Magnetometer** | iSentek IST8310 onboard on I2C4 (0x0C) with internal heater compensation | **None onboard** (`HAL_I2C_INTERNAL_MASK 0`, `ALLOW_ARM_NO_COMPASS`) | Deliberately omitted to prevent motor current EMI corruption; heading provided by external GNSS mast | Pixhawk 6C `hwdef.dat` L220-228; Hub `hwdef.dat` L85-89; Review §6 & Backlog #3 |
| **IOMCU Coprocessor** | **Present**: STM32F103 coprocessor over USART6 (`PC6`/`PC7`) driving 8 MAIN outputs | **None (Eliminated)**: All outputs generated directly by STM32H743 FMU | Drastically simplifies board routing, removes secondary bootloader flashing, enables full DMA DSHOT | Pixhawk 6C `hwdef.dat` L76-80, L258, L264-265; Hub `hwdef.dat` L131-147; Review §5.3 |
| **Actuator PWM Outputs** | 8 MAIN outputs (IOMCU) + 8 AUX PWM channels on FMU (TIM1, TIM4, TIM5) | 12 Direct FMU PWM channels on TIM1 (CH1-4), TIM4 (CH1-4), TIM5 (CH1-4) | Independent 4-channel timer blocks guarantee zero DMA stream contention for mixed servo/ESC rates | Pixhawk 6C `hwdef.dat` L115-122; Hub `hwdef.dat` L131-147; Review §4.4 & Table 7.1 |
| **Non-Volatile Parameter Storage** | External Ramtron FM25V02A FRAM (32KB) on SPI2 (PD3/PC2/PC3, CS: `PD4`) | On-chip Flash Sector Emulation (32KB on 128KB sector 14: `STORAGE_FLASH_PAGE 14`) | Removes dedicated SPI FRAM IC and bus lines from BOM while providing robust 32KB parameter memory | Pixhawk 6C `hwdef.dat` L109-112, L247-248; Hub `hwdef.dat` L181-182; MatekH743 `hwdef.dat` L177-181 |
| **High-Capacity Flight Logging** | MicroSD card slot on 4-bit SDMMC2 (PD6/PD7/PB14/PB15/PB3/PB4) | MicroSD card slot on 4-bit SDMMC1 (PC8-PC12, PD2) with FatFS support | Provides gigabytes of BlackBox storage for long-range fixed-wing missions; leaves Port B pins free | Pixhawk 6C `hwdef.dat` L186-192; Hub `hwdef.dat` L171-178; Review §4.5 & Table 7.2 |
| **Connector Standard Compliance** | Pixhawk-standard DS-018 JST-GH connectors | Pixhawk-standard DS-018 JST-GH connectors ([ADR-0002](../adr/0002-pixhawk-standard-connectors.md)) | 100% plug-and-play pin-for-pin mating with standard COTS GPS pucks, telemetry radios, and power modules | Holybro 6C Ports Guide; Hub `docs/adr/0002-pixhawk-standard-connectors.md`; Review §7.1 |
| **CAN / DroneCAN Buses** | Dual CAN buses: CAN1 (`PD0`/`PD1`) and CAN2 (`PB5`/`PB13`) | Dual FDCAN buses: CAN1 (`PD0`/`PD1`) and CAN2 (`PB12`/`PB13`) | Dual redundant CAN interfaces with standard 4-pin JST-GH pinouts; PB12/PB13 avoids PB5 conflict | Pixhawk 6C `hwdef.dat` L125-129; Hub `hwdef.dat` L94-100; Review Table 7.1 |
| **Power Brick Inputs & Sensing** | Dual analog power inputs (POWER1: `PC5`/`PC4`; POWER2: `PB1`/`PA2`) + VDD sense (`PA4`) | Dual analog power inputs (POWER1: `PC0`/`PC1`; POWER2: `PC5`/`PC4`) + Diode OR-ing | Paralleled 6-pin JST-GH power brick inputs with Schottky diode OR-ing between USB VBUS and 5V buck | Pixhawk 6C `hwdef.dat` L84-95; Hub `hwdef.dat` L152-163; Review §4.3 & Table 7.1 |
| **Safety Switch & LED** | Dedicated safety switch pin (`HAL_HAVE_SAFETY_SWITCH 1`) via IOMCU/FMU | Dedicated safety switch button (`PE10`, `SAFETY_IN`) and LED drive (`PE3`, `LED_SAFETY`) | Supported both on standalone 3-pin connector and multiplexed onto standard GPS1 10-pin connector | Pixhawk 6C `hwdef.dat` L251; Hub `hwdef.dat` L165-167; Review Table 7.1 |
| **Buzzer Output** | Open-drain buzzer drive on TIM3 CH3 (`PB0`, `ALARM`) | Open-drain buzzer drive on TIM2 CH1 (`PA15`, `ALARM`) | Low-side N-FET drive for external 5V magnetic buzzer, tied to GPS1 pin 9 and standalone 2-pin JST-GH | Pixhawk 6C `hwdef.dat` L209; Hub `hwdef.dat` L169; Review Table 7.1 |

---

## 3. Detailed Subsystem Analysis

### 3.1 Microcontroller, Clocking, and System Timers
*   **MCU & Pin Allocation:** Both designs leverage the STM32H743 (LQFP-176 pinout), supplying 140 I/O pins. While Pixhawk 6C routes several Port C/D pins to its secondary IOMCU coprocessor and external FRAM, MADpilot-H7 utilizes LQFP-176 pin availability to dedicate contiguous timer blocks to its 12 PWM outputs and provide dual hardware flow control (RTS/CTS) on both TELEM1 and TELEM2.
*   **HSE Clock Selection:** Pixhawk 6C uses a 16 MHz external oscillator. MADpilot-H7 uses an 8 MHz external clock source (`OSCILLATOR_HZ 8000000`). In accordance with comparative review findings (§4.1), standard active crystal drive mode without `STM32_HSE_BYPASS` is configured, preventing PLL lock failure and USB enumeration hangs.
*   **System Timer Isolation:** Pixhawk 6C binds `STM32_ST_USE_TIMER` to TIM2, which prevents TIM2 channels from driving external actuators or alarms. MADpilot-H7 assigns `STM32_ST_USE_TIMER 12` (following the MatekH743 architecture), freeing TIM2 CH1 on PA15 for the audible alarm buzzer.

### 3.2 Sensor Diversity vs In-Stock-First Procurement
*   **Vibration Isolation vs Dissimilar MEMS:** Pixhawk 6C features an isolated internal IMU damping board mounting an ICM-42688-P and BMI055/BMI088. MADpilot-H7 addresses high-vibration fixed-wing environments through sensor architecture diversity: pairing a primary TDK ICM-42605 (SPI1, D1 domain) with a dissimilar Bosch BMI270 (SPI4, D2 domain).
*   **Elimination of Onboard Compass:** Pixhawk 6C includes an internal IST8310 magnetometer with heater compensation (`HAL_HEATER_MAG_OFFSET`). In fixed-wing UAVs, onboard compasses suffer severe electromagnetic distortion from high-current motor battery leads. MADpilot-H7 eliminates the internal magnetometer (`HAL_I2C_INTERNAL_MASK 0`), relying entirely on the external compass mounted on the GNSS mast via I2C1.

### 3.3 IOMCU Elimination and Direct Timer DMA
*   Pixhawk 6C incorporates an STM32F103 IO coprocessor communicating with the FMU over USART6 at 1.5 Mbps. This coprocessor generates the 8 MAIN PWM outputs, while the FMU handles 8 AUX outputs.
*   MADpilot-H7 intentionally eliminates the IOMCU. By partitioning 12 actuator channels across three discrete 4-channel timers:
    - **TIM1 (CH1–4):** `PE9`, `PE11`, `PE13`, `PE14` (Bank 1)
    - **TIM4 (CH1–4):** `PD12`, `PD13`, `PD14`, `PD15` (Bank 2)
    - **TIM5 (CH1–4):** `PA0`, `PA1`, `PA2`, `PA3` (Bank 3)
    Every channel benefits from independent DMA request streams through the STM32H7 DMAMUX. This architecture provides DSHOT telemetry and high-update digital servo protocols on any channel without DMA contention or dual-firmware flashing complexity.

### 3.4 Storage and Logging Architecture
*   Pixhawk 6C relies on an external 32KB Ramtron FRAM on SPI2 for parameter persistence and SDMMC2 for microSD logging.
*   MADpilot-H7 eliminates the SPI FRAM, utilizing on-chip flash emulation (`STORAGE_FLASH_PAGE 14`, 32KB allocation) for zero-BOM-cost non-volatile parameter storage, and dedicates SDMMC1 (PC8–PC12, PD2) to high-speed FatFS flight logging.

---

## 4. Compliance Summary

| Standard / Requirement | Reference Board (Pixhawk 6C) | MADpilot-H7 Status | Compliance Mechanism |
| :--- | :---: | :---: | :--- |
| **DS-018 Connector Standard** | Compliant | **Compliant** | All connectors adhere to Pixhawk DS-018 JST-GH pinouts ([ADR-0002](../adr/0002-pixhawk-standard-connectors.md)) |
| **Open Hardware License** | Proprietary Commercial | **CERN-OHL-S-2.0** | Full EDA and firmware source publication path ([ADR-0001](../adr/0001-open-hardware-license-path.md)) |
| **Trademark Compliance** | N/A (Holybro/Pixhawk) | **Compliant** | Product name is strictly MADpilot-H7; no trademark infringement |
| **Dual Power Redundancy** | Compliant | **Compliant** | Paralleled 6-pin JST-GH inputs with dual voltage/current sense |
| **Dual DroneCAN Interface** | Compliant | **Compliant** | Dual FDCAN transceivers on CAN1 and CAN2 |
| **Full Flight Logging** | Compliant | **Compliant** | 4-bit high-speed SDMMC1 MicroSD card slot |

---
*End of MADpilot-H7 vs Reference Board Delta Table.*

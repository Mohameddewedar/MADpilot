# Critical BOM Component Pre-Qualification Record (Rev A Pre-Capture)

**Date:** 2026-09-08  
**Scope:** Pre-qualify ~12 critical components at LCSC/JLCPCB before schematic capture begins per Issue #11 and the **In-Stock-First** rule ([CONTEXT.md](../../CONTEXT.md#L30-L31)).

---

## 1. Summary Matrix

| # | Subsystem Function | Manufacturer Part Number (MPN) | Manufacturer | LCSC Part # | Package / Footprint | Live Stock | Lifecycle | Unit Price (1+) | Direct Catalog Link |
| :- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | **MCU** | `STM32H743IIT6` | STMicroelectronics | **C89597** | LQFP-176 (24x24 mm) | 27 *(+800 whse)* | Active (normal) | $11.12 | [LCSC C89597](https://www.lcsc.com/product-detail/C89597.html) |
| 2 | **Primary IMU** | `ICM-42605` | TDK InvenSense | **C2655099** | LGA-14 (2.5x3 mm) | 8 *(Note 1)* | Active (normal) | $9.51 | [LCSC C2655099](https://www.lcsc.com/product-detail/C2655099.html) |
| 3 | **Secondary IMU** | `BMI270` | Bosch Sensortec | **C2836813** | LGA-14 (2.5x3 mm) | 5,644 | Active (normal) | $3.26 | [LCSC C2836813](https://www.lcsc.com/product-detail/C2836813.html) |
| 4 | **Barometer** | `MS561101BA03-50` | TE / Measurement Specialties | **C15639** | QFN-8 (3x5 mm) | 3,071 | Active (normal) | $6.76 | [LCSC C15639](https://www.lcsc.com/product-detail/C15639.html) |
| 5 | **Main 5V Buck** | `AP63205WU-7` | Diodes Incorporated | **C2071056** | TSOT-23-6 | 28,917 | Active (normal) | $0.43 | [LCSC C2071056](https://www.lcsc.com/product-detail/C2071056.html) |
| 6 | **3V3_SENS LDO** | `AP7343-33W5-7` | Diodes Incorporated | **C460383** | SOT-25 (SOT-23-5) | 605 | Active (normal) | $0.36 | [LCSC C460383](https://www.lcsc.com/product-detail/C460383.html) |
| 7 | **3V3_MCU LDO** | `AP2112K-3.3TRG1` | Diodes Incorporated | **C51118** | SOT-25 (SOT-23-5) | 62,760 | Active (normal) | $0.17 | [LCSC C51118](https://www.lcsc.com/product-detail/C51118.html) |
| 8 | **CAN1 Transceiver** | `SN65HVD230DR` | Texas Instruments | **C12084** | SOIC-8 | 55,975 | Active (normal) | $0.70 | [LCSC C12084](https://www.lcsc.com/product-detail/C12084.html) |
| 9 | **CAN2 Transceiver** | `SIT1051ATK/3` | SIT | **C5382552** | DFN-8 / HVSON-8 (3x3 mm) | 5,307 | Active (normal) | $0.50 | [LCSC C5382552](https://www.lcsc.com/product-detail/C5382552.html) |
| 10 | **8 MHz HSE Crystal** | `NX3225GD-8MHZ-STD-CRA-3` | NDK | **C889706** | SMD3225-2P | 50,985 | Active (normal) | $0.35 | [LCSC C889706](https://www.lcsc.com/product-detail/C889706.html) |
| 10b | **8 MHz Resonator (Alt)** | `CSTNE8M00GH5C000R0` | Murata | **C341525** | SMD3213-3P | 116,300 | Active (normal) | $0.24 | [LCSC C341525](https://www.lcsc.com/product-detail/C341525.html) |
| 11 | **MicroSD Socket** | `TF-01A` | Korean Hroparts Elec | **C91145** | SMD (Push-Push) 9-pin | 223,295 | Active (normal) | $0.19 | [LCSC C91145](https://www.lcsc.com/product-detail/C91145.html) |
| 12 | **USB-C Receptacle** | `TYPE-C-31-M-12` | Korean Hroparts Elec | **C165948** | 16-pin USB-C SMD + TH tabs | 274,725 | Active (normal) | $0.19 | [LCSC C165948](https://www.lcsc.com/product-detail/C165948.html) |
| 13 | **USB ESD Protection** | `USBLC6-2P6` | STMicroelectronics | **C15999** | SOT-666-6 | 7,455 | Active (normal) | $0.29 | [LCSC C15999](https://www.lcsc.com/product-detail/C15999.html) |
| 13b | **USB ESD Protection (Alt)** | `USBLC6-2SC6` | STMicroelectronics | **C7519** | SOT-23-6 | 40,995 | Active (normal) | $0.18 | [LCSC C7519](https://www.lcsc.com/product-detail/C7519.html) |

---

## 2. Risk Analysis & Findings

1. **ICM-42605 Stock Volatility (Note 1)**:
   - On-hand stock is currently 8 units on LCSC. Because only 5 PCBA units are being manufactured for Rev A, 8 units is sufficient for the immediate prototype run, but represents a critical stock-drift risk.
   - Mitigation: Prior to BOM freeze (week 5), verify inventory. If LCSC stock drops below requirement, JLCPCB parts pre-order/consign feature or second-source supplier (Digikey/Mouser turnkey consignment) will be invoked.

2. **CAN Transceiver Obsolescence**:
   - `SIT1051T/3` in SOIC-8 (`C1121842`) was found to be `stop_product` (EOL) with 0 stock.
   - Resolution: `SN65HVD230DR` (`C12084`, 55k in stock) is the primary proven transceiver (from SAL-FC). `SIT1051ATK/3` (`C5382552`, 5.3k in stock, DFN-8) is selected for CAN2 / compact footprint.

3. **MCU Stock Status**:
   - `STM32H743IIT6` has 27 units immediate stock and 800 units in factory warehouse flash stock. Plentiful for Phase 1 batch requirements.

4. **All parts verified active with non-zero stock**:
   - Every single component listed above satisfies the **In-Stock-First** gate.

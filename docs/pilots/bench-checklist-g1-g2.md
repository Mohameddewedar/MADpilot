# MADpilot Flight Controller — Bench Bring-Up Checklist (Gates G1–G2)

This document provides the canonical bench bring-up and verification checklist for the **MADpilot Flight Controller (FC)**. It guides pilots and bench engineers step-by-step through the validation criteria required to pass **Phase Gate G1** (bench bring-up) and **Phase Gate G2** (Rev A complete) as defined in [PLAN.md](../../PLAN.md#phase-gates).

Vocabulary strictly adheres to [CONTEXT.md](../../CONTEXT.md). Connector pinning adheres to the Pixhawk-standard connector specification defined in [ADR-0002](../adr/0002-pixhawk-standard-connectors.md). Equipment and bench tool references correspond to [EQUIPMENT.md](../EQUIPMENT.md).

---

## 1. Pre-Bench Setup & Equipment

Before applying power to the Flight Controller, prepare the physical workspace, tools, and build artifacts.

### 1.1 Required Bench Tools & Hardware

- [ ] **Flight Controller Under Test**: Phase-0 Matek H743-Wing development board or custom MADpilot-H7 Flight Controller board.
- [ ] **SWD Debugger / Programmer**: ST-Link V2 (or clone) / Segger J-Link with 4-pin SWD cable (`SWDIO`, `SWCLK`, `GND`, `3.3V/Vtarget`).
- [ ] **PC Interface Cable**: High-quality USB-C data cable (verify data lines are wired, not a charge-only cable).
- [ ] **Telemetry Radio Pair**:
  - Air radio connected to the Flight Controller `TELEM1` JST-GH connector ([ADR-0002](../adr/0002-pixhawk-standard-connectors.md)).
  - Ground radio connected to GCS laptop via USB.
  - Frequencies must comply with the approved **Radio Allowance** ([CONTEXT.md](../../CONTEXT.md)): SiK 433 MHz, 915 MHz, or 2.4 GHz ESP32 WiFi bridge.
- [ ] **GNSS Puck**: External M9N-class GNSS receiver with integrated compass, connected to `GPS1` / `I2C` JST-GH ports.
- [ ] **Actuator Test Rig**: 4x standard PWM hobby servos (Aileron, Elevator, Throttle channel, Rudder) or mounted foam-trainer control surfaces.
  > [!WARNING]
  > **PROPELLER REMOVAL**: Ensure all motor propellers are completely removed during bench testing. Never install a propeller on the bench.
- [ ] **Bench Power Supply & Power Module**:
  - Regulated bench DC power supply (30 V / 5 A class) with current limit set to 1.0 A, OR a dedicated 3S LiPo battery (11.1 V nominal) with an in-line fuse/current limiter.
  - Pixhawk-standard power module connected to `POWER1`.
  - 5 V BEC to power the servo rail if not powered by the internal Flight Controller BEC.
- [ ] **Digital Multimeter (DMM) / Oscilloscope**: For measuring 5 V and 3.3 V power rails under load.
- [ ] **Ground Control Station (GCS)**: Laptop running Mission Planner (recommended for firmware operations) or QGroundControl.

### 1.2 Firmware Artifact Sourcing (CI Pipeline)

The Flight Controller firmware and bootloader binaries must be sourced directly from the reproducible repository CI build:

1. Navigate to the GitHub repository **Actions** tab: [MADpilot CI](../../.github/workflows/ci.yml).
2. Select the latest successful workflow run on branch `main`.
3. Under the **Artifacts** section, locate and download:
   - **`MatekH743-madpilot-plane-artifacts`** (for the OEM target with foam-trainer defaults).
   - *(Note: `MatekH743-plane-artifacts` is also generated for standard base-board builds).*
4. Extract the `.zip` archive to verify the presence of:
   - `AP_Bootloader.bin` — ArduPilot bootloader binary for the STM32H743.
   - `arduplane.apj` — ArduPlane firmware JSON package with embedded ROMFS defaults.
   - `arduplane.bin` — Raw firmware binary.

---

## 2. Phase Gate G1 — Bench Bring-Up Checklist

> Reference: [PLAN.md Phase Gates](../../PLAN.md#phase-gates) — **G1**: *"boots via SWD, bootloader flashed, GCS link over USB and telemetry, all sensors live, actuator sweep"*

### Step G1.1: SWD Bootloader Flashing

Because fresh or unprogrammed STM32H743 boards do not carry a pre-flashed bootloader, initial bring-up must occur via Serial Wire Debug (SWD).

- [ ] **Wire the SWD Interface**:
  - Connect ST-Link `SWDIO` -> FC `SWD_DIO`
  - Connect ST-Link `SWCLK` -> FC `SWD_CLK`
  - Connect ST-Link `GND` -> FC `GND`
  - Connect ST-Link `3.3V` (or `VAPP`) -> FC `3.3V` (target voltage sense)
- [ ] **Flash the Bootloader (`AP_Bootloader.bin`)**:

  **Canonical Command (STM32CubeProgrammer CLI)**:
  ```bash
  STM32_Programmer_CLI -c port=SWD mode=UR -w AP_Bootloader.bin 0x08000000 -v -rst
  ```

  **Alternative 1 (OpenOCD)**:
  ```bash
  openocd -f interface/stlink.cfg -f target/stm32h7x.cfg \
    -c "init; reset halt; flash write_image erase AP_Bootloader.bin 0x08000000; reset run; exit"
  ```

  **Alternative 2 (st-flash)**:
  ```bash
  st-flash --reset write AP_Bootloader.bin 0x08000000
  ```

- **Pass/Fail Criterion**:
  - **PASS**: Programmer CLI outputs `Flash memory erased`, `Download verified successfully`, and triggers reset. Flight Controller status LED indicates bootloader activity (rapid cyclic blinking pattern waiting for application code).
  - **FAIL**: Target voltage not detected, SWD communication failure, flash verification mismatch, or unresponsive MCU.

---

### Step G1.2: Application Firmware Flashing via GCS

With the bootloader active, install the application firmware package (`arduplane.apj`) over USB.

- [ ] Disconnect SWD header. Connect Flight Controller to PC using USB-C cable.
- [ ] Open Mission Planner (do **NOT** click Connect).
- [ ] Navigate to **Setup** -> **Install Firmware**.
- [ ] Click **Load custom firmware** in the bottom-right corner.
- [ ] Select the extracted **`arduplane.apj`** from the CI artifact directory.
- [ ] Allow the uploader to erase flash, program sectors, and verify checksums.
- **Pass/Fail Criterion**:
  - **PASS**: Progress bar completes to 100%, GCS displays `Upload Succeeded!`, and the Flight Controller reboots automatically.
  - **FAIL**: Uploader cannot establish bootloader handshake, times out during flash erase, or CRC verification fails.

---

### Step G1.3: First Boot over USB & GCS Link Verification

- [ ] Select the virtual COM port assigned to the Flight Controller in Mission Planner / QGroundControl (baud rate `115200`). Click **Connect**.
- [ ] **Verify MADpilot Custom Firmware String**:
  - In Mission Planner HUD / Messages tab or terminal banner, verify the firmware identification string contains:
    ```text
    MADpilot
    ```
    *(Defined in `hwdef.dat` via `AP_CUSTOM_FIRMWARE_STRING "MADpilot"`).*
- [ ] **Verify ROM'd Lua Announcer Message**:
  - Inspect the GCS **Messages** console immediately following boot.
  - Confirm receipt of the severity-6 (`MAV_SEVERITY_INFO`) announcement generated by `madpilot_announce.lua`:
    ```text
    MADpilot OEM online [Batt: XX.XXV (XX%)]
    ```
    *(If powered only via USB without flight battery connected, the announcer displays `MADpilot OEM online [Battery: N/A]`).*
- **Pass/Fail Criterion**:
  - **PASS**: MAVLink connection establishes within 5 seconds; GCS HUD displays attitude and telemetry; firmware string confirms `MADpilot`; Lua announcer status message appears in message log.
  - **FAIL**: Flight Controller fails to boot, enters hard fault loop, hangs during parameter table loading, or displays generic unbranded firmware strings.

---

### Step G1.4: Telemetry Link Verification over Serial Radio

- [ ] Disconnect USB cable from Flight Controller.
- [ ] Connect air radio to `TELEM1` JST-GH connector ([ADR-0002](../adr/0002-pixhawk-standard-connectors.md)). Power the Flight Controller via `POWER1` from bench power supply.
- [ ] Plug ground radio into PC. Note assigned COM port.
- [ ] In GCS, select the radio COM port and set baud rate to `57600` baud. Click **Connect**.
- [ ] Monitor telemetry stream for 60 seconds.
- **Pass/Fail Criterion**:
  - **PASS**: Telemetry connects wirelessly; full parameter tree loads over the air; link quality indicator reports `Rx Quality > 80%`; live telemetry updates at >2 Hz.
  - **FAIL**: Radio handshake fails, packets drop continuously, parameter download hangs, or link quality drops below 60% on bench.

---

### Step G1.5: Live Sensors Verification

Verify that all essential flight sensors report live, calibrated, and physically responsive data in the GCS:

- [ ] **Dual IMUs (Gyroscopes & Accelerometers)**:
  - Physically pitch, roll, and yaw the Flight Controller.
  - Verify artificial horizon on GCS HUD moves smoothly and counteracts physical tilt (tilt nose down -> horizon moves up; roll right -> horizon tilts left).
  - Inspect `VIBE` and `RAW_IMU` graphs: accelerometers read ~9.81 m/s² on Z-axis when resting flat.
- [ ] **Barometer**:
  - Verify indicated relative altitude is stable (±0.5 m drift maximum while stationary).
  - Gently blow toward the barometer sensor or seal in a small enclosure; verify instantaneous altitude fluctuation and recovery.
- [ ] **GNSS Puck**:
  - Place GNSS puck near window or outdoors.
  - Verify GPS status advances from `NoGPS` -> `GPS Lock` (3D Fix, HDOP < 1.5, Satellite count ≥ 8).
- [ ] **External Magnetometer (Compass)**:
  - Note: MADpilot-H7 Rev A has **no onboard magnetometer** per [PLAN.md](../../PLAN.md#improvement-backlog); compass is provided by the external GNSS puck over I2C/CAN.
  - Slowly rotate the GNSS puck 360 degrees. Verify heading dial on GCS HUD rotates synchronously without hanging or flipping 180 degrees.
  - Verify pre-arm status does not report `PreArm: Compass not calibrated`.
- **Pass/Fail Criterion**:
  - **PASS**: All sensor health flags show green in GCS pre-arm checklist; HUD tracking accurately mirrors physical movement; GPS locks; compass tracks cleanly.
  - **FAIL**: `Bad Gyro Health`, `Baro Glitch`, `Compass Inconsistent`, or sensor read timeouts reported.

---

### Step G1.6: Actuator Sweep

- [ ] Connect 4 standard servos to the Flight Controller PWM outputs:
  - Output 1: Primary Aileron / Roll control surface
  - Output 2: Elevator / Pitch control surface
  - Output 3: Throttle ESC / Motor signal (*motor unpowered or propeller removed!*)
  - Output 4: Rudder / Yaw control surface
- [ ] Power servo rail with 5.0 V BEC.
- [ ] In Mission Planner, navigate to **Setup** -> **Optional Hardware** -> **Motor/Servo Test**, OR bind RC receiver to test stick movement in `MANUAL` mode:
  - Command Roll Left: verify aileron deflection moves left surface UP, right surface DOWN.
  - Command Pitch Up: verify elevator deflection moves UP.
  - Command Yaw Right: verify rudder deflection moves RIGHT.
  - Command Throttle: verify PWM signal sweeps smoothly from 1000 µs to 2000 µs.
- **Pass/Fail Criterion**:
  - **PASS**: All 4 actuator channels respond smoothly without jitter, dead zones, reversed deflection, or mechanical binding.
  - **FAIL**: Any servo fails to respond, stutters, reverses intended aerodynamic direction, or draws excessive current causing servo rail sag.

---

### Step G1.7: OEM Failsafe Defaults Sanity Check

Open **Config/Tuning** -> **Full Parameter List** in Mission Planner. Confirm that all OEM parameters defined in `defaults.parm` (verified by CI smoke test in [scripts/sitl_smoke.py](../../scripts/sitl_smoke.py)) are present and strictly match expected values:

| Parameter | Expected OEM Default | Purpose | Verified |
|---|---|---|:---:|
| `FS_GCS_ENABL` | `1` | Enable GCS telemetry link-loss failsafe | [ ] |
| `FS_LONG_ACTN` | `1` | Return-To-Launch (RTL) upon long failsafe trigger | [ ] |
| `FS_LONG_TIMEOUT` | `5` | 5 seconds of telemetry loss before RTL engages | [ ] |
| `BATT_MONITOR` | `4` | Analog voltage and current monitoring enabled | [ ] |
| `BATT_CAPACITY` | `2200` | 2200 mAh pack capacity (foam-trainer fleet) | [ ] |
| `BATT_LOW_VOLT` | `10.5` | 10.5 V (3.5 V/cell) low voltage threshold -> RTL | [ ] |
| `BATT_CRT_VOLT` | `10.0` | 10.0 V (3.33 V/cell) critical voltage threshold -> RTL | [ ] |
| `BATT_LOW_MAH` | `440` | 440 mAh (20% capacity reserve) -> RTL | [ ] |
| `BATT_CRT_MAH` | `220` | 220 mAh (10% capacity reserve) -> RTL | [ ] |
| `BATT_FS_LOW_ACT` | `1` | RTL action on low battery | [ ] |
| `BATT_FS_CRT_ACT` | `1` | RTL action on critical battery | [ ] |
| `BATT_ARM_VOLT` | `11.1` | 11.1 V minimum voltage required to arm | [ ] |
| `SCR_ENABLE` | `1` | Lua scripting engine enabled for OEM announcer | [ ] |

- **Pass/Fail Criterion**:
  - **PASS**: Every listed parameter matches the OEM default table exactly; no failsafe is disabled (`0`).
  - **FAIL**: Any failsafe parameter is reset to unconfigured ArduPilot defaults (e.g., `FS_GCS_ENABL = 0` or `BATT_MONITOR = 0`).

---

## 3. Phase Gate G2 — Rev A Complete Checklist

> Reference: [PLAN.md Phase Gates](../../PLAN.md#phase-gates) — **G2**: *"Rev A complete: full sensor set logging on a vibration-realistic mount, no brownouts, current draw within budget"*

### Step G2.1: Sensor Logging on Vibration-Realistic Mount

- [ ] Secure the Flight Controller onto a vibration-damping mount (silicone bobbins or high-density foam dampening pads) inside the test airframe or vibration test jig.
- [ ] Connect microSD card into the onboard SD card slot.
- [ ] Set parameter `LOG_DISARMED = 1` temporarily to record data on the bench without arming safety locks.
- [ ] Run motor vibration sweep:
  - Run the propulsion motor through 0% -> 25% -> 50% -> 75% -> 100% throttle increments on a rigid test stand (with a balanced propeller or unbalanced test weight if safely contained).
  - Run the sweep for a minimum of 180 seconds.
- [ ] Disarm / power down and extract the latest `.BIN` dataflash log file from the SD card.
- [ ] Set `LOG_DISARMED = 0` to restore standard flight logging behavior.

---

### Step G2.2: Dataflash Log (`.BIN`) Health & Vibration Audit

Open the `.BIN` log file in Mission Planner (**Flight Data** -> **DataFlash Logs** -> **Review a Log**):

- [ ] **Vibration Clipping (`VIBE.Clip0`, `Clip1`, `Clip2`)**:
  - Inspect clipping counts across the entire duration of the throttle sweep.
  - Requirement: **0 clipping events** permitted.
- [ ] **Vibration Acceleration Amplitudes (`VIBE.VibeX`, `VibeY`, `VibeZ`)**:
  - Peak vibration levels must remain strictly below **30 m/s²** at all throttle levels (target: < 15 m/s²).
- [ ] **Dual IMU Consistency & Sample Rate**:
  - Graph `IMU[0]` and `IMU[1]` accelerometer and gyroscope traces.
  - Verify both IMUs (ICM-42605 and BMI270 per [PLAN.md Phase 1](../../PLAN.md#phase-1--rev-a-m2m6)) log continuously at the 400 Hz fast loop rate.
  - Confirm **0 dropped packets**, 0 driver restart messages in `MSG`, and zero EKF primary IMU lane switches.
- [ ] **Barometer & Bus Logging**:
  - Graph `BARO.Alt` and verify absence of high-frequency electrical hash or spikes correlating with motor ESC commutation.
- **Pass/Fail Criterion**:
  - **PASS**: `.BIN` log shows 0 vibration clipping events, peak vibration amplitudes < 30 m/s², both IMU logs populated without drops, and EKF status is healthy throughout the run.
  - **FAIL**: Non-zero clipping count, excessive vibration (>30 m/s²), IMU dropout or driver panic, or corrupted log structure.

---

### Step G2.3: Power Rail Stress & Brownout Immunity Verification

The Flight Controller must withstand peak servo actuation and transient bus loads without suffering MCU brownout resets or voltage dips on internal logic rails.

- [ ] **Setup Measurement Points**:
  - Probe `5V_SERVO` rail (servo bus) with DMM / oscilloscope.
  - Probe internal `VDD_5V` and `VDD_3V3` test points on the Flight Controller.
- [ ] **Static Quiescent Current Check**:
  - Power Flight Controller, GNSS puck, and telemetry radio via bench power supply set to 12.0 V (simulating 3S LiPo).
  - Measure quiescent supply current:
    - Expected current budget: **180 mA – 320 mA** at 12 V.
    - Confirm current draw is within budget.
- [ ] **Dynamic Actuator Stress Sweep**:
  - Command all 4 servos simultaneously into rapid cyclic motion (full-throw stick stirring in `MANUAL` mode at maximum slew rate for 60 seconds).
  - Apply physical resistive load to servo arms (simulating aerodynamic airloads).
  - Observe oscilloscope trace on `VDD_5V` and `VDD_3V3`:
    - Maximum allowable voltage sag on 5 V rail: **≥ 4.80 V**.
    - Maximum allowable ripple/sag on 3.3 V MCU rail: **≥ 3.25 V**.
- [ ] **Brownout Reset Audit**:
  - Confirm the Flight Controller MCU does not reset, reboot, or lose MAVLink heartbeat during peak servo stall/sweep.
  - Inspect `STATUSTEXT` log for any brownout warnings or hardware watchdog reboots (`WDG` reset flag).
- **Pass/Fail Criterion**:
  - **PASS**: Voltage remains strictly above 4.80 V (5 V rail) and 3.25 V (3.3 V rail); current draw remains within power module design limits; zero resets or reboots observed.
  - **FAIL**: Any MCU reset occurs, MAVLink disconnects during servo movement, or 5 V rail collapses below 4.75 V.

---

### Step G2.4: External Compass & Sensor Architecture Confirmation

- [ ] Confirm that no onboard magnetometer is present or enabled on the Flight Controller PCB, strictly preserving the design choice in [PLAN.md](../../PLAN.md#improvement-backlog) (Backlog entry #3).
- [ ] Verify `COMPASS_DEV_ID` identifies the external GNSS puck magnetometer as Compass 1 via I2C or DroneCAN.
- [ ] Verify internal compass instances are disabled (`COMPASS_ENABLE = 1`, `COMPASS_USE = 1` for external only).
- **Pass/Fail Criterion**:
  - **PASS**: External compass operates cleanly with 0 I2C bus error increments (`I2C.Errors = 0` in telemetry status).
  - **FAIL**: System attempts to access a non-existent internal magnetometer or generates bus hang errors.

---

## 4. Phase Gate G1–G2 Pilot Sign-Off Summary

Before proceeding to pre-taxi simulation testing ([docs/pilots/pre-taxi-runbook.md](pre-taxi-runbook.md)), the pilot and lead engineer must review and sign this gate declaration:

| Verification Gate | Requirement | Status | Date Verified | Sign-off Initials |
|---|---|:---:|:---:|:---:|
| **Gate G1** | SWD bootloader flashed & verified | PASS / FAIL | | |
| **Gate G1** | `MADpilot` firmware string verified | PASS / FAIL | | |
| **Gate G1** | Lua announcer `"MADpilot OEM online"` received | PASS / FAIL | | |
| **Gate G1** | Telemetry link stable (>80% quality) | PASS / FAIL | | |
| **Gate G1** | All sensors live (IMU/Baro/GPS/Compass) | PASS / FAIL | | |
| **Gate G1** | Actuator sweep passed (4 channels) | PASS / FAIL | | |
| **Gate G1** | OEM failsafes configured (`FS_GCS_ENABL=1`, `BATT_*`) | PASS / FAIL | | |
| **Gate G2** | Sensor logging on vibration mount (0 clips) | PASS / FAIL | | |
| **Gate G2** | Dual IMU logging verified at 400 Hz | PASS / FAIL | | |
| **Gate G2** | Brownout test passed (rail ≥4.8V under load) | PASS / FAIL | | |
| **Gate G2** | Current draw within budget (<350 mA quiescent) | PASS / FAIL | | |

**Gate Exit Determination**:
- [ ] **G1 & G2 APPROVED**: Flight Controller hardware, bootloader, sensors, and power systems are verified Sell-Ready and bench-certified. Authorized to proceed to [Pre-Taxi Simulation-on-Hardware Runbook](pre-taxi-runbook.md).
- [ ] **G1 / G2 REJECTED**: Hardware anomalies or parameter defects detected. Return Flight Controller to bench diagnostics.

**Lead Pilot Signature**: ___________________________ &nbsp;&nbsp;&nbsp;&nbsp; **Date**: _______________

# MADpilot Flight Controller — Pre-Taxi Runbook (Gate G3 Entry)

This runbook establishes the mandatory verification protocol required before authorizing any aircraft taxi test (**Phase Gate G3**) under the MADpilot program.

> Reference: [PLAN.md Phase Gates](../../PLAN.md#phase-gates) — **G3**: *"taxi"*
>
> **Core Rule**: **Gate G3 never starts with untested firmware.** Every Flight Controller board revision or firmware release must complete the bench bring-up checklist ([docs/pilots/bench-checklist-g1-g2.md](bench-checklist-g1-g2.md)) and execute the **Simulation-on-Hardware ritual** before taxiing under its own power.

Vocabulary strictly adheres to [CONTEXT.md](../../CONTEXT.md). All connector interfaces follow [ADR-0002](../adr/0002-pixhawk-standard-connectors.md).

---

## 1. Flash-from-CI Workflow

Operational firmware binaries must be obtained directly from automated CI build runs to ensure reproducibility, auditability, and Sell-Ready compliance. Do not flash arbitrary local or untracked test builds for taxi or flight operations.

### 1.1 Downloading Build Artifacts

The CI workflow defined in [.github/workflows/ci.yml](../../.github/workflows/ci.yml) builds the ArduPlane firmware and bootloader for each supported board target and validates OEM defaults via the SITL smoke test.

#### Option A: GitHub Web Interface
1. Open the repository on GitHub and navigate to the **Actions** tab.
2. Under **All workflows**, select the latest successful run of **`MADpilot CI`** on branch `main`.
3. Scroll to the **Artifacts** section at the bottom of the summary page.
4. Click and download the artifact:
   - **`MatekH743-madpilot-plane-artifacts`** (carries custom `"MADpilot"` firmware string, foam-trainer fleet defaults, and ROM'd Lua boot announcer).
   - *(Note: `MatekH743-plane-artifacts` contains upstream base-board builds for comparison).*
5. Unpack the downloaded `.zip` archive on the GCS laptop:
   ```text
   MatekH743-madpilot-plane-artifacts/
   ├── AP_Bootloader.bin
   ├── arduplane.apj
   └── arduplane.bin
   ```

#### Option B: GitHub CLI (`gh`) One-Liner
From a terminal with `gh` authenticated:
```bash
# Download latest artifacts from the most recent successful run of MADpilot CI
gh run download $(gh run list --workflow="MADpilot CI" --status=success --limit 1 --json databaseId --jq '.[0].databaseId') \
  --name "MatekH743-madpilot-plane-artifacts" \
  --dir ./firmware-latest
```

---

### 1.2 Flashing `arduplane.apj` via Ground Control Station (GCS)

With the bootloader already installed (completed during Gate G1), flash the application package via USB:

1. Connect the Flight Controller to the GCS laptop using a USB-C data cable.
2. Launch **Mission Planner** (do **NOT** click Connect in the top-right).
3. Navigate to **Setup** -> **Install Firmware**.
4. In the bottom-right corner, click **Load custom firmware**.
5. Browse to the extracted folder and select **`arduplane.apj`**.
6. Mission Planner detects the ArduPilot bootloader, transmits the firmware package, verifies sector checksums, and prompts `Upload Succeeded!`.
7. The Flight Controller automatically reboots into the updated application.
8. Connect at **115200 baud** over USB or **57600 baud** over telemetry radio:
   - Verify the GCS HUD/Messages tab displays the OEM branding string:
     ```text
     MADpilot
     ```
   - Verify receipt of the ROM'd Lua announcer statustext:
     ```text
     MADpilot OEM online [Batt: ...]
     ```

---

## 2. Simulation-on-Hardware Ritual

### 2.1 What Simulation-on-Hardware Does

Simulation-on-hardware (`sitl-on-hw`) is ArduPilot's in-silico validation tool. Rather than running a desktop SITL binary on a PC, `sitl-on-hw` compiles a specialized firmware binary configured with `SIM_ENABLED 1` that is flashed directly onto the physical STM32H7 microcontroller of the Flight Controller:

- **Hardware Execution**: The physical MCU executes the real ChibiOS real-time operating system (RTOS), ArduPilot scheduling loops (`SCHED_LOOP_RATE 400`), thread synchronization, and memory management.
- **Sensor Driver Substitution**: Real physical sensor backends (IMUs, barometer, GPS receiver) are replaced by internal mathematical simulation models (`AHRS_EKF_TYPE 10`, `GPS1_TYPE 100`) running directly inside the firmware.
- **Physical Communication Interfaces Active**: Hardware UARTs, USB CDC serial, telemetry links (`TELEM1`), and status LEDs remain active and driven by the physical hardware.
- **Why It Is Mandatory**: It proves that the exact compiled flight guidance algorithms, state machine transitions, failsafe logic, and MAVLink telemetry handlers execute cleanly on the target silicon under dynamic flight dynamics before putting physical propellers on the bench or wheels on the runway.

### 2.2 When Simulation-on-Hardware is Required

Running the simulation-on-hardware ritual is **MANDATORY**:
- Before the first taxi (**Gate G3**) of any newly assembled or brought-up Flight Controller board (e.g. Rev A / Rev B).
- Before testing any new firmware build or parameter default overhaul on the test airframe.
- Whenever changes are made to core failsafe logic (`FS_GCS_ENABL`, `FS_LONG_ACTN`, `BATT_*`).

---

### 2.3 Concrete Build and Upload Command

From the root of the initialized `ardupilot` repository checkout:

```bash
python3 Tools/scripts/sitl-on-hardware/sitl-on-hw.py \
  --board MatekH743-madpilot \
  -v plane \
  --defaults libraries/AP_HAL_ChibiOS/hwdef/MatekH743-madpilot/defaults.parm \
  --upload
```

#### Command-Line Flags Reference
- **`--board <board>`**: Specifies the target hardware definition. Use `MatekH743-madpilot` (or `MatekH743` for the raw base dev board, `MADpilotH7` for custom silicon).
- **`-v plane`, `--vehicle plane`** *(required)*: Targets the fixed-wing flight vehicle (`ArduPlane`).
- **`--defaults <path>`**: Injects the project's OEM default parameter file (`defaults.parm`) so the simulation boots with link-loss RTL and 3S LiPo battery failsafes active.
- **`--upload`**: Automatically invokes the ArduPilot uploader over USB virtual serial upon build completion, uploading the `.apj` directly to the Flight Controller.
- *(Optional)* **`-f <frame>`**: Specifies vehicle frame type if testing non-standard aerodynamic configurations.
- *(Optional)* **`--simclass <class>`**: Specifies simulation physics class (e.g. `Glider`).

---

### 2.4 Ritual Verification Steps: What a Successful Run Looks Like

Follow this step-by-step procedure during the simulation-on-hardware run:

- [ ] **Step 1: Boot into Simulation Mode**
  - Upon upload completion, the Flight Controller reboots running `sitl-on-hw`.
  - Connect the Flight Controller via USB (`115200 baud`) or telemetry radio (`57600 baud`) to Mission Planner / QGroundControl.
- [ ] **Step 2: Attitude & Synthetic GNSS Verification**
  - Verify the GCS artificial horizon initializes level.
  - Verify synthetic GPS lock acquires (default SITL coordinates, e.g., Canberra CMAC location or configured home point).
  - Verify aircraft status displays `EKF: OK` (using SITL AHRS `AHRS_EKF_TYPE = 10`).
- [ ] **Step 3: Arming & Takeoff Sequence**
  - Set vehicle mode to `TAKEOFF` or `AUTO` with a simple test mission (takeoff, 2 waypoints, loiter).
  - Issue ARM command via GCS or bound RC transmitter.
  - Verify motor synthetic throttle commands engage, synthetic airspeed accelerates past `AIRSPEED_MIN` (10 m/s), and aircraft lifts off on the GCS map.
- [ ] **Step 4: Flight Guidance & Waypoint Tracking**
  - Observe simulated aircraft navigating between waypoints at `AIRSPEED_CRUISE` (15 m/s).
  - Verify roll limits (`ROLL_LIMIT_DEG = 35°`) and pitch limits (`PTCH_LIM_MAX_DEG = 20°`, `PTCH_LIM_MIN_DEG = -15°`) are respected by the flight controller.
- [ ] **Step 5: Telemetry Link-Loss Failsafe Assertion**
  - While the simulated aircraft is en route, physically disconnect the telemetry ground radio or kill the GCS connection.
  - After `FS_LONG_TIMEOUT` (5 seconds), observe that the flight mode transitions autonomously to **`RTL`** (Return-To-Launch per `FS_LONG_ACTN = 1`).
  - Reconnect GCS and verify the aircraft returns to the launch location and loiters at `RTL_ALTITUDE` (50 m).
- [ ] **Step 6: Battery Failsafe Assertion**
  - Using the MAVLink parameter interface or simulated battery drain, allow simulated battery voltage to drop below `BATT_LOW_VOLT` (10.5 V).
  - Verify Flight Controller triggers low battery failsafe and commands **`RTL`** (`BATT_FS_LOW_ACT = 1`).

---

### 2.5 Restoring Operational Flight Firmware

> [!IMPORTANT]
> **DO NOT ATTEMPT TO TAXI OR FLY WITH SITL-ON-HW FIRMWARE!**
> `sitl-on-hw` firmware overrides real sensor inputs with simulated physics. Real flight requires the release firmware package.

Once the simulation ritual is verified:
1. Reconnect the Flight Controller via USB.
2. In Mission Planner (**Setup** -> **Install Firmware** -> **Load custom firmware**), reflash the clean operational **`arduplane.apj`** sourced from the CI artifact (`MatekH743-madpilot-plane-artifacts`).
3. Reconnect GCS and confirm physical sensors respond to board movement ([docs/pilots/bench-checklist-g1-g2.md](bench-checklist-g1-g2.md) Step G1.5).

---

## 3. Phase Gate G3 Taxi Authorization Sign-Off

The pilot and safety officer must verify all checkboxes below before wheel movement or taxi testing is authorized on the tarmac.

### 3.1 Verification Checklist

- [ ] **Bench Bring-Up Verified**:
  - [Bench Checklist G1–G2](bench-checklist-g1-g2.md) fully executed and signed off.
  - Power rail stability verified (5 V rail ≥ 4.80 V under maximum servo stress; 0 brownout resets).
  - Dual IMU logging verified on vibration mount with 0 clipping events.
- [ ] **Simulation-on-Hardware Ritual Verified**:
  - `sitl-on-hw.py` executed successfully on this Flight Controller unit.
  - Simulated waypoint mission flown without attitude divergence or EKF faults.
  - Link-loss failsafe verified (5s timeout -> RTL).
  - Battery failsafe verified (10.5 V -> RTL).
- [ ] **Operational Firmware Restored & Verified**:
  - CI artifact `MatekH743-madpilot-plane-artifacts` flashed onto the Flight Controller.
  - Firmware branding string confirmed in GCS banner: `MADpilot`.
  - ROM'd Lua announcer confirmed in GCS messages: `MADpilot OEM online [Batt: ...]`.
- [ ] **Airframe Taxi Readiness**:
  - External GNSS puck and compass mounted securely and oriented forward.
  - Actuator sweep confirmed on physical control surfaces (correct direction, zero binding).
  - Propeller securely tightened; taxi area clear of bystanders and debris.

---

### 3.2 Authorization Table

| Criterion | Requirement | Result | Pilot Initials |
|---|---|:---:|:---:|
| **Gate G1 & G2** | Bench bring-up & vibration test complete | PASS / FAIL | |
| **Sim-on-Hardware** | In-silico validation & failsafe test complete | PASS / FAIL | |
| **Firmware Identity** | `MADpilot` custom string confirmed in GCS | PASS / FAIL | |
| **Lua Boot Announcer** | `"MADpilot OEM online"` statustext confirmed | PASS / FAIL | |
| **Failsafe Settings** | `FS_GCS_ENABL=1`, `FS_LONG_ACTN=1`, `BATT_FS_LOW_ACT=1` | PASS / FAIL | |
| **Physical Pre-Arm** | All GCS pre-arm sensors reporting green | PASS / FAIL | |

**Gate G3 Taxi Determination**:
- [ ] **AUTHORIZED FOR TAXI (GATE G3 ENTRY)**: The Flight Controller, firmware, and airframe satisfy all prerequisites. The pilot is authorized to power the aircraft and conduct low-speed taxi trials.
- [ ] **REJECTED / GROUNDED**: Prerequisites incomplete or failsafe discrepancy detected. Aircraft remains grounded.

**Lead Pilot Signature**: ___________________________ &nbsp;&nbsp;&nbsp;&nbsp; **Date**: _______________
**Safety Officer Signature**: _________________________ &nbsp;&nbsp;&nbsp;&nbsp; **Date**: _______________

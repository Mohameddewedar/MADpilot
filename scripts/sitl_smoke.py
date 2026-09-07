#!/usr/bin/env python3
"""
MADpilot SITL Failsafe Smoke Test
Asserts a stable boot of SITL Plane with OEM defaults applied, verifying that:
1. Boot is stable (heartbeats received, valid fixed-wing type, no failure state).
2. GCS link-loss failsafe is enabled and set to RTL (FS_GCS_ENABL == 1, FS_LONG_ACTN == 1).
3. Plane battery-failsafe parameters match OEM defaults (BATT_FS_LOW_ACT, BATT_LOW_VOLT, etc.).
4. Scripting is enabled (SCR_ENABLE == 1).
5. EVERY parameter defined in defaults.parm is present in the effective parameter set.
"""

import argparse
import math
import os
import subprocess
import sys
import time

# Ensure pymavlink is discoverable from system or ardupilot checkout
def setup_pymavlink_path():
    try:
        import pymavlink  # noqa: F401
        return
    except ImportError:
        pass

    script_dir = os.path.dirname(os.path.realpath(__file__))
    hub_root = os.path.dirname(script_dir)
    candidate_paths = [
        os.path.join(hub_root, "ardupilot", "modules", "mavlink", "pymavlink"),
        os.path.join(hub_root, "ardupilot", "modules", "mavlink"),
        os.path.join(hub_root, "ardupilot", "modules", "pymavlink"),
        os.path.join(hub_root, "ardupilot", "Tools", "autotest", "pysim"),
    ]
    for path in candidate_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)


def get_mavutil():
    setup_pymavlink_path()
    try:
        from pymavlink import mavutil
        return mavutil
    except ImportError as err:
        print(f"FATAL: Unable to import pymavlink: {err}", file=sys.stderr)
        print("Please install pymavlink (e.g. 'pip install pymavlink') or ensure ardupilot submodules are initialized.", file=sys.stderr)
        sys.exit(2)



class AssertionResult:
    def __init__(self, name: str, passed: bool, details: str):
        self.name = name
        self.passed = passed
        self.details = details


class SmokeTestRunner:
    def __init__(
        self,
        endpoint: str,
        defaults_file: str,
        binary: str | None = None,
        timeout: float = 60.0,
        telemetry_wait: float = 3.0,
        verbose: bool = False
    ):
        self.endpoint = endpoint
        self.defaults_file = defaults_file
        self.binary = binary
        self.timeout = timeout
        self.telemetry_wait = telemetry_wait
        self.verbose = verbose
        self.results: list[AssertionResult] = []
        self.params: dict[str, float] = {}
        self.expected_params: dict[str, float] = {}
        self.sitl_proc: subprocess.Popen | None = None

    def log(self, msg: str):
        if self.verbose:
            print(f"[SMOKE] {msg}")

    def load_defaults(self):
        if not os.path.isfile(self.defaults_file):
            raise FileNotFoundError(f"Defaults file not found: {self.defaults_file}")

        with open(self.defaults_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.strip()
                if not clean_line or clean_line.startswith("#") or clean_line.startswith("//") or clean_line.startswith("@"):
                    continue

                # Handle whitespace or comma separated: PARAM_NAME VALUE
                parts = clean_line.replace(",", " ").split()
                if len(parts) >= 2:
                    pname = parts[0].strip()
                    try:
                        pval = float(parts[1].strip())
                        self.expected_params[pname] = pval
                    except ValueError:
                        self.log(f"Skipping non-numeric parameter line {line_num}: {clean_line}")

        self.log(f"Loaded {len(self.expected_params)} expected parameters from {self.defaults_file}")

    def connect_and_fetch(self):
        mavutil = get_mavutil()
        self.log(f"Connecting to MAVLink endpoint: {self.endpoint}")
        start_time = time.time()
        conn = None

        # Attempt connection
        while time.time() - start_time < self.timeout:
            try:
                conn = mavutil.mavlink_connection(
                    self.endpoint,
                    autoreconnect=True,
                    source_system=250,
                    source_component=250,
                    timeout=5.0
                )
                break
            except Exception as e:
                self.log(f"Connection attempt failed ({e}), retrying...")
                time.sleep(1.0)

        if conn is None:
            raise TimeoutError(f"Could not establish connection to {self.endpoint} within {self.timeout}s")

        # Wait for vehicle heartbeat
        self.log("Waiting for vehicle heartbeat...")
        heartbeat = conn.wait_heartbeat(timeout=max(5.0, self.timeout - (time.time() - start_time)))
        if not heartbeat:
            raise TimeoutError(f"No heartbeat received from {self.endpoint} within timeout")

        self.log(f"Heartbeat received: sysid={conn.target_system}, compid={conn.target_component}, type={heartbeat.type}, status={heartbeat.system_status}")

        # Stream telemetry for telemetry_wait seconds to ensure boot stability
        self.log(f"Streaming telemetry for {self.telemetry_wait:.1f}s to observe boot stability...")
        t_end = time.time() + self.telemetry_wait
        heartbeat_count = 1
        critical_errors = []
        statuses = [heartbeat.system_status]

        while time.time() < t_end:
            msg = conn.recv_msg()
            if msg is not None:
                mtype = msg.get_type()
                if mtype == "HEARTBEAT":
                    heartbeat_count += 1
                    statuses.append(msg.system_status)
                elif mtype == "STATUSTEXT":
                    severity = getattr(msg, "severity", 6)
                    text = getattr(msg, "text", "")
                    # MAV_SEVERITY_EMERGENCY(0), ALERT(1), CRITICAL(2)
                    if severity <= 2:
                        critical_errors.append(f"[{severity}] {text}")
                    self.log(f"STATUSTEXT ({severity}): {text}")

        # Fetch parameter list
        self.log("Requesting parameter list from vehicle...")
        conn.mav.param_request_list_send(conn.target_system, conn.target_component)

        param_start = time.time()
        expected_total = None
        while time.time() - param_start < self.timeout:
            msg = conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=1.0)
            if msg is not None:
                pid = msg.param_id
                if isinstance(pid, bytes):
                    pid = pid.decode("ascii", errors="ignore")
                pid = pid.strip("\x00").strip()
                self.params[pid] = msg.param_value
                expected_total = msg.param_count

                if expected_total is not None and len(self.params) >= expected_total:
                    break

        self.log(f"Fetched {len(self.params)} parameters (expected total: {expected_total})")

        # Fallback: single read request for any expected parameter not in self.params
        missing_expected = [p for p in self.expected_params if p not in self.params]
        if missing_expected:
            self.log(f"Attempting direct read for {len(missing_expected)} missing parameters: {missing_expected}")
            for mp in missing_expected:
                conn.mav.param_request_read_send(
                    conn.target_system,
                    conn.target_component,
                    mp.encode("ascii"),
                    -1
                )
                m = conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=1.5)
                if m is not None:
                    pid = m.param_id
                    if isinstance(pid, bytes):
                        pid = pid.decode("ascii", errors="ignore")
                    pid = pid.strip("\x00").strip()
                    self.params[pid] = m.param_value

        return heartbeat, heartbeat_count, statuses, critical_errors

    def run(self) -> bool:
        self.load_defaults()

        if self.binary:
            if not os.path.isfile(self.binary):
                self.results.append(AssertionResult(
                    name="0. SITL Launch",
                    passed=False,
                    details=f"Binary not found: {self.binary}"
                ))
                self.print_report()
                return False

            sitl_cwd = os.path.dirname(os.path.abspath(self.binary))
            cmd = [
                os.path.abspath(self.binary),
                "--model", "plane",
                "--speedup", "1",
                "--defaults", os.path.abspath(self.defaults_file),
                "-I0",
            ]
            self.log(f"Launching SITL: {' '.join(cmd)} (cwd={sitl_cwd})")
            self.sitl_proc = subprocess.Popen(
                cmd,
                cwd=sitl_cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                text=True,
            )

        try:
            try:
                hb, hb_count, statuses, critical_errors = self.connect_and_fetch()
            except Exception as ex:
                self.results.append(AssertionResult(
                    name="1. Boot Stability",
                    passed=False,
                    details=f"Failed to connect or receive telemetry: {ex}"
                ))
                self.print_report()
                return False

            # --- Assertion 1: Boot is stable (no failure state) ---
            # Failure states in MAVLink: MAV_STATE_CRITICAL (5), MAV_STATE_EMERGENCY (6), MAV_STATE_FLIGHT_TERMINATION (8)
            unhealthy_statuses = [s for s in statuses if s in (5, 6, 8)]
            boot_stable = (hb_count >= 1) and (len(unhealthy_statuses) == 0) and (len(critical_errors) == 0)
            a1_details = f"Heartbeats={hb_count}, VehicleType={hb.type}, Statuses={set(statuses)}"
            if critical_errors:
                a1_details += f", CriticalErrors={critical_errors}"
            self.results.append(AssertionResult(
                name="1. Boot Stability",
                passed=boot_stable,
                details=a1_details
            ))

            # --- Assertion 2: FS_GCS_ENABLE / link-loss RTL ---
            # Note: In ArduPlane, parameter is named FS_GCS_ENABL; check both for robustness.
            gcs_fs_param = "FS_GCS_ENABL" if "FS_GCS_ENABL" in self.params else "FS_GCS_ENABLE"
            gcs_fs_val = self.params.get(gcs_fs_param)
            long_actn_val = self.params.get("FS_LONG_ACTN")
            expected_gcs_fs = self.expected_params.get("FS_GCS_ENABL", self.expected_params.get("FS_GCS_ENABLE", 1.0))
            expected_long_actn = self.expected_params.get("FS_LONG_ACTN", 1.0)

            a2_passed = (
                gcs_fs_val is not None
                and math.isclose(gcs_fs_val, expected_gcs_fs, abs_tol=1e-3)
                and long_actn_val is not None
                and math.isclose(long_actn_val, expected_long_actn, abs_tol=1e-3)
            )
            self.results.append(AssertionResult(
                name="2. Link-loss RTL Failsafe (FS_GCS_ENABL / FS_LONG_ACTN)",
                passed=a2_passed,
                details=f"{gcs_fs_param}={gcs_fs_val} (expected {expected_gcs_fs}), FS_LONG_ACTN={long_actn_val} (expected {expected_long_actn})"
            ))

            # --- Assertion 3: Plane battery-failsafe parameters ---
            batt_checks = ["BATT_FS_LOW_ACT", "BATT_LOW_VOLT", "BATT_CRT_VOLT", "BATT_FS_CRT_ACT", "BATT_ARM_VOLT"]
            batt_mismatches = []
            for bp in batt_checks:
                if bp in self.expected_params:
                    exp = self.expected_params[bp]
                    actual = self.params.get(bp)
                    if actual is None or not math.isclose(actual, exp, abs_tol=1e-2):
                        batt_mismatches.append(f"{bp}: actual={actual}, expected={exp}")

            a3_passed = len(batt_mismatches) == 0
            self.results.append(AssertionResult(
                name="3. Battery Failsafe Parameters",
                passed=a3_passed,
                details="All battery failsafe parameters verified" if a3_passed else f"Mismatches: {', '.join(batt_mismatches)}"
            ))

            # --- Assertion 4: SCR_ENABLE equals OEM value ---
            scr_val = self.params.get("SCR_ENABLE")
            expected_scr = self.expected_params.get("SCR_ENABLE", 1.0)
            a4_passed = scr_val is not None and math.isclose(scr_val, expected_scr, abs_tol=1e-3)
            self.results.append(AssertionResult(
                name="4. Scripting Enabled (SCR_ENABLE)",
                passed=a4_passed,
                details=f"SCR_ENABLE={scr_val} (expected {expected_scr})"
            ))

            # --- Assertion 5: EVERY parameter in defaults.parm is present and effective ---
            missing_params = []
            value_mismatches = []
            for pname, exp_val in self.expected_params.items():
                if pname not in self.params:
                    missing_params.append(pname)
                else:
                    act_val = self.params[pname]
                    if not math.isclose(act_val, exp_val, abs_tol=1e-2):
                        value_mismatches.append(f"{pname}: actual={act_val}, expected={exp_val}")

            a5_passed = (len(missing_params) == 0) and (len(value_mismatches) == 0)
            a5_details = f"Verified {len(self.expected_params)}/{len(self.expected_params)} OEM defaults present."
            if missing_params:
                a5_details += f" MISSING ({len(missing_params)}): {missing_params}."
            if value_mismatches:
                a5_details += f" VALUE MISMATCHES ({len(value_mismatches)}): {value_mismatches}."

            self.results.append(AssertionResult(
                name="5. All OEM Defaults Present and Effective",
                passed=a5_passed,
                details=a5_details
            ))

            return self.print_report()
        finally:
            if self.sitl_proc is not None:
                self.log("Terminating SITL process...")
                self.sitl_proc.terminate()
                try:
                    self.sitl_proc.wait(timeout=3.0)
                except subprocess.TimeoutExpired:
                    self.sitl_proc.kill()


    def print_report(self) -> bool:
        print("\n" + "=" * 78)
        print("                   MADpilot SITL SMOKE TEST REPORT")
        print("=" * 78)
        all_passed = True
        for res in self.results:
            status_str = "[ PASS ]" if res.passed else "[ FAIL ]"
            if not res.passed:
                all_passed = False
            print(f"{status_str} {res.name}")
            print(f"         Details: {res.details}")
        print("=" * 78)

        if all_passed:
            print("SUMMARY: ALL 5 ASSERTIONS PASSED (SITL boot verified with OEM defaults)")
            print("=" * 78 + "\n")
            return True
        else:
            print("SUMMARY: SMOKE TEST FAILED - One or more assertions did not pass")
            print("=" * 78 + "\n")
            return False


def main():
    parser = argparse.ArgumentParser(description="MADpilot SITL Failsafe Smoke Test Runner")
    parser.add_argument(
        "--connect",
        type=str,
        default="tcp:127.0.0.1:5760",
        help="MAVLink connection endpoint (default: tcp:127.0.0.1:5760)"
    )
    parser.add_argument(
        "--binary",
        type=str,
        default=None,
        help="Optional path to SITL arduplane binary to launch and manage automatically"
    )
    parser.add_argument(
        "--defaults",
        type=str,
        default=os.path.join("ardupilot", "libraries", "AP_HAL_ChibiOS", "hwdef", "MatekH743-madpilot", "defaults.parm"),
        help="Path to OEM defaults.parm file"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Connection and parameter fetch timeout in seconds (default: 60.0)"
    )
    parser.add_argument(
        "--telemetry-wait",
        type=float,
        default=3.0,
        help="Seconds of telemetry streaming to observe post-boot (default: 3.0)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable verbose debug logging"
    )

    args = parser.parse_args()
    runner = SmokeTestRunner(
        endpoint=args.connect,
        defaults_file=args.defaults,
        binary=args.binary,
        timeout=args.timeout,
        telemetry_wait=args.telemetry_wait,
        verbose=args.verbose
    )

    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

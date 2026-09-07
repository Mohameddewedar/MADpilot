# Release Staging — ArduPilot GPLv3 Source Offer

This directory documents the **GNU General Public License Version 3 (GPLv3)** source-offer compliance obligations for MADpilot-H7 firmware, and provides the draft written-offer text accompanying physical board shipments.

Per [ADR-0001](../../docs/adr/0001-open-hardware-license-path.md) and [ADR-0004](../../docs/adr/0004-hub-repo-fork-submodule.md), the MADpilot-H7 firmware is derived from ArduPilot (specifically stable Plane), which is licensed under GNU GPLv3. The hub repository incorporates ArduPilot as a pinned git submodule. When any MADpilot-H7 Flight Controller is sold or distributed with compiled binary firmware (bootloader or flight controller binary), GPLv3 Section 6 mandates providing or offering the Complete Corresponding Source Code.

---

## What Must Be Offered

In accordance with GPLv3 Section 6 ("Conveying Non-Source Forms"), the source offer package must convey the **Complete Corresponding Source Code** required to generate, install, and run the exact binary firmware flashed onto the shipped Flight Controller.

The complete offer package comprises:

1. **The Exact ArduPilot Pinned Fork Commit**:
   - The exact Git commit hash of the ArduPilot repository submodule (`ardupilot` submodule ref) corresponding to the build flashed onto the board.
   - Publicly accessible git remote URL (e.g. `https://github.com/Mohameddewedar/ardupilot.git`).

2. **Hub Repository OEM Layer & Hardware Definitions**:
   - Board hardware definition files (`hwdef.dat` and `hwdef-bl.dat` for `MADpilotH7`).
   - Default vehicle parameter sets (`defaults.parm`).
   - Board identity configuration (`AP_CUSTOM_FIRMWARE_STRING "MADpilot"`, `APJ_BOARD_ID 3141`, USB VID `0x1D50` / PID).
   - CI and build scripts used to compile the target binary (`Tools/scripts/build_bootloaders.py`, waf build commands).

3. **Toolchain & Build Instructions**:
   - Explicit, reproducible build instructions detailing:
     - Target OS (e.g. Ubuntu LTS).
     - Cross-compiler toolchain and exact version (`arm-none-eabi-gcc`).
     - Python environment and prerequisite packages.
     - Exact commands executed to configure and build both the bootloader (`Tools/scripts/build_bootloaders.py MADpilotH7`) and the flight firmware (`./waf configure --board MADpilotH7`, `./waf plane`).

4. **License Texts**:
   - Full copy of the GNU General Public License Version 3 ([release/licenses/GPL-3.0.txt](../licenses/GPL-3.0.txt)).
   - Top-level repository license notice.

---

## Draft Written Offer Text

The following written offer must accompany every physical shipment of MADpilot-H7 hardware, either printed on product documentation, included in packaging, or clearly referenced in shipment paperwork per GPLv3 Section 6(b):

```text
================================================================================
                    WRITTEN OFFER FOR SOURCE CODE
================================================================================

Product: MADpilot-H7 Flight Controller
Firmware: Derived from ArduPilot (GNU General Public License Version 3)

This product contains software and firmware licensed under the GNU General
Public License Version 3 (GPLv3).

In accordance with Section 6(b) of the GNU GPLv3, we hereby offer to provide
you, upon request, with a complete machine-readable copy of the Corresponding
Source code for the software and firmware contained in this product, on a
durable physical medium customarily used for software interchange, for a charge
no more than our reasonable cost of physically performing this conveying of
source, or at no charge via network access.

This offer is valid for at least three (3) years from the date you received
this product, or for as long as we offer spare parts or customer support for
this product model.

To obtain the source code:
1. Online repository:
   https://github.com/Mohameddewedar/MADpilot
   Pinned ArduPilot submodule: https://github.com/Mohameddewedar/ardupilot
   Target build commit / release tag: [INSERT_FIRMWARE_GIT_COMMIT_OR_TAG]

2. Direct request by mail or electronic mail:
   Email: release@madpilot.dev (or project contact listed in repository)
   Please specify: "MADpilot-H7 Source Code Request", including your board
   serial/batch number and date of receipt.

A copy of the GNU General Public License Version 3 is included with this product
documentation and available at:
https://www.gnu.org/licenses/gpl-3.0.txt
================================================================================
```

---

## Automated Packaging Tool

To assemble the release source-offer package automatically at release time, use the helper script:
[make_source_package.py](make_source_package.py)

This script verifies that the ArduPilot submodule is initialized, inspects the pinned commit SHA, bundles the license texts and instructions, and outputs an offer manifest.

#!/usr/bin/env python3
"""
make_source_package.py - Assemble GPLv3 source offer package for MADpilot-H7.

Collects licenses, documentation, build instructions, and submodule commit
manifest into a standalone, dated release package directory.
"""

import argparse
import datetime
import os
from pathlib import Path
import shutil
import subprocess
import sys


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def check_submodule_initialized(repo_root: Path) -> str:
    """Verify ardupilot submodule is initialized and return its checked-out commit."""
    submodule_dir = repo_root / "ardupilot"
    if not (submodule_dir / ".git").exists() and not (submodule_dir / ".git").is_file():
        # Check via git submodule status
        res = subprocess.run(
            ["git", "submodule", "status", "ardupilot"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        status_line = res.stdout.strip()
        if status_line.startswith("-") or res.returncode != 0:
            sys.exit(
                "Error: ardupilot submodule is not initialized.\n"
                "Run 'git submodule update --init --recursive' before building the source package."
            )

    # Get checked out commit
    res = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(submodule_dir),
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        sys.exit(
            "Error: Failed to obtain ardupilot submodule commit.\n"
            "Run 'git submodule update --init --recursive' first."
        )
    return res.stdout.strip()


def get_gitmodules_info(repo_root: Path) -> str:
    gitmodules = repo_root / ".gitmodules"
    if gitmodules.is_file():
        return gitmodules.read_text(encoding="utf-8").strip()
    return "No .gitmodules file found."


def get_hub_commit(repo_root: Path) -> str:
    res = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    return res.stdout.strip() if res.returncode == 0 else "unknown"


def build_instructions_text(submodule_commit: str, hub_commit: str) -> str:
    return f"""MADpilot-H7 Firmware Build Instructions (GPLv3 Source Package)
==============================================================

To rebuild the exact binary firmware shipped on the MADpilot-H7 board:

1. Prerequisites:
   - Linux host (e.g. Ubuntu 22.04 LTS or 24.04 LTS)
   - Python 3.8+ with pip
   - GNU Arm Embedded Toolchain (arm-none-eabi-gcc 10.3-2021.10 or compatible)
   - Git, make, ccache

2. Clone ArduPilot and checkout pinned commit:
   git clone https://github.com/Mohameddewedar/ardupilot.git
   cd ardupilot
   git checkout {submodule_commit}
   git submodule update --init --recursive

3. Install ArduPilot build prerequisites:
   ./Tools/environment_install/install-prereqs-ubuntu.sh -y
   . ~/.profile

4. Build Bootloader:
   ./Tools/scripts/build_bootloaders.py MADpilotH7
   # Outputs: Tools/bootloaders/MADpilotH7_bl.bin and .hex

5. Build Plane Firmware:
   ./waf configure --board MADpilotH7
   ./waf plane
   # Output: build/MADpilotH7/bin/arduplane.apj

Hub repo commit reference: {hub_commit}
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assemble GPLv3 source offer package for MADpilot-H7."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Target output directory (default: release/source-offer/packages/<YYYY-MM-DD>)",
    )
    args = parser.parse_args()

    repo_root = get_repo_root()

    # Step 1: Submodule verification (fails early if uninitialized)
    submodule_commit = check_submodule_initialized(repo_root)

    # Step 2: Determine output directory
    today = datetime.date.today().isoformat()
    out_dir = args.out or (repo_root / "release" / "source-offer" / "packages" / today)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Step 3: Copy licenses and docs
    shutil.copy2(repo_root / "LICENSE", out_dir / "LICENSE")
    shutil.copy2(repo_root / "release" / "licenses" / "GPL-3.0.txt", out_dir / "GPL-3.0.txt")
    shutil.copy2(repo_root / "release" / "source-offer" / "README.md", out_dir / "SOURCE-OFFER.md")

    # Step 4: Write instructions and manifest
    hub_commit = get_hub_commit(repo_root)
    (out_dir / "BUILD_INSTRUCTIONS.txt").write_text(
        build_instructions_text(submodule_commit, hub_commit), encoding="utf-8"
    )

    manifest_content = f"""MADpilot-H7 Source Offer Package Manifest
Package Date: {today}
Hub Repository Commit: {hub_commit}
ArduPilot Submodule Commit: {submodule_commit}

.gitmodules Configuration:
{get_gitmodules_info(repo_root)}

Package Contents:
- LICENSE (Hub repository license)
- GPL-3.0.txt (Full GNU General Public License Version 3)
- SOURCE-OFFER.md (Source offer terms and draft written offer)
- BUILD_INSTRUCTIONS.txt (Reproducible build steps)
- MANIFEST.txt (This manifest)
"""
    (out_dir / "MANIFEST.txt").write_text(manifest_content, encoding="utf-8")

    print(f"Source offer package successfully assembled at: {out_dir}")


if __name__ == "__main__":
    main()

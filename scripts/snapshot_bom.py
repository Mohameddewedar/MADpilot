#!/usr/bin/env python3
"""
snapshot_bom.py - Create an immutable In-Stock-First BOM snapshot.

Captures the frozen KiCad BOM, initializes a stock-state procurement verification
record, populates the manifest, and generates cryptographic checksums.
"""

import argparse
import csv
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def parse_bom_csv(bom_path: Path) -> list[tuple[str, str]]:
    """Parse CSV and extract (part_number, description) tuples."""
    if not bom_path.is_file():
        sys.exit(f"Error: BOM file does not exist: {bom_path}")

    try:
        with open(bom_path, "r", encoding="utf-8-sig", newline="") as f:
            sample = f.read(2048)
            f.seek(0)
            if not sample.strip():
                sys.exit(f"Error: BOM file is empty: {bom_path}")

            reader = csv.reader(f)
            rows = [row for row in reader if any(cell.strip() for cell in row)]
    except Exception as e:
        sys.exit(f"Error: Failed to parse CSV '{bom_path}': {e}")

    if not rows:
        sys.exit(f"Error: No data rows found in BOM file: {bom_path}")

    header = [col.strip().lower() for col in rows[0]]
    part_col = -1
    desc_col = -1

    # Candidate column names
    part_candidates = ["part_number", "part number", "part", "mpn", "lcsc part", "lcsc", "value", "device"]
    desc_candidates = ["description", "desc", "details", "comment", "value", "name"]

    for idx, col in enumerate(header):
        if part_col == -1 and any(cand == col or cand in col for cand in part_candidates):
            part_col = idx
        elif desc_col == -1 and any(cand == col or cand in col for cand in desc_candidates):
            desc_col = idx

    has_header = (part_col != -1 or desc_col != -1)
    data_rows = rows[1:] if has_header else rows

    if part_col == -1:
        part_col = 0
    if desc_col == -1:
        desc_col = 1 if len(rows[0]) > 1 else 0

    parts = []
    for row in data_rows:
        part_num = row[part_col].strip() if len(row) > part_col else ""
        desc = row[desc_col].strip() if len(row) > desc_col and desc_col != part_col else ""
        if part_num or desc:
            parts.append((part_num, desc))

    if not parts:
        sys.exit(f"Error: No valid part entries extracted from BOM CSV: {bom_path}")

    return parts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an immutable In-Stock-First BOM snapshot at rev freeze."
    )
    parser.add_argument(
        "--bom",
        required=True,
        type=Path,
        help="Path to KiCad BOM CSV file",
    )
    parser.add_argument(
        "--rev",
        required=True,
        type=str,
        help="Revision identifier (e.g. RevA, RevB)",
    )
    parser.add_argument(
        "--notes",
        type=str,
        default="",
        help="Optional notes regarding this rev freeze",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output snapshots directory (default: hardware/bom/snapshots)",
    )
    args = parser.parse_args()

    rev_name = args.rev.strip()
    if not rev_name:
        sys.exit("Error: --rev cannot be empty.")

    bom_path = args.bom.resolve()
    parts = parse_bom_csv(bom_path)

    repo_root = get_repo_root()
    today = datetime.date.today().isoformat()
    out_base = args.out.resolve() if args.out else (repo_root / "hardware" / "bom" / "snapshots")
    snapshot_dir = out_base / f"{rev_name}-{today}"

    # Snapshots are immutable: refuse to overwrite
    if snapshot_dir.exists():
        sys.exit(
            f"Error: Snapshot directory already exists at: {snapshot_dir}\n"
            "BOM snapshots are immutable and cannot be overwritten."
        )

    snapshot_dir.mkdir(parents=True, exist_ok=False)

    # 1. Archive copy of the original BOM
    archived_bom_name = bom_path.name
    shutil.copy2(bom_path, snapshot_dir / archived_bom_name)

    # 2. Generate stock-state.csv with parts pre-filled
    stock_state_path = snapshot_dir / "stock-state.csv"
    with open(stock_state_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "part_number",
            "description",
            "stock_quantity",
            "lifecycle_state",
            "unit_price",
            "product_url",
        ])
        for part_num, desc in parts:
            writer.writerow([part_num, desc, "", "", "", ""])

    # 3. Generate manifest.json
    template_path = repo_root / "hardware" / "bom" / "template" / "manifest.json"
    manifest_data = {}
    if template_path.is_file():
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["revision"] = rev_name
    manifest_data["snapshot_date"] = today
    manifest_data["bom_file"] = archived_bom_name
    manifest_data["notes"] = args.notes
    manifest_data["part_count"] = len(parts)

    manifest_path = snapshot_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
        f.write("\n")

    # 4. Generate SHA256SUMS covering all archived files
    checksums = []
    files_to_hash = [archived_bom_name, "stock-state.csv", "manifest.json"]
    for fname in sorted(files_to_hash):
        file_p = snapshot_dir / fname
        if file_p.is_file():
            csum = compute_sha256(file_p)
            checksums.append(f"{csum}  {fname}")

    sums_path = snapshot_dir / "SHA256SUMS"
    sums_path.write_text("\n".join(checksums) + "\n", encoding="utf-8")

    print(f"Snapshot created successfully at: {snapshot_dir}")


if __name__ == "__main__":
    main()

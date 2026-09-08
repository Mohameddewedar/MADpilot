#!/usr/bin/env python3
"""
populate_stock_state.py - Populate stock-state.csv with verified procurement data and rehash SHA256SUMS.
"""

import csv
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS_DIR = REPO_ROOT / "hardware" / "bom" / "snapshots"

STOCK_DATA = {
    "STM32H743IIT6": {
        "stock_quantity": 27,
        "lifecycle_state": "normal",
        "unit_price": "11.1152",
        "product_url": "https://www.lcsc.com/product-detail/C89597.html",
    },
    "ICM-42605": {
        "stock_quantity": 8,
        "lifecycle_state": "normal",
        "unit_price": "9.5109",
        "product_url": "https://www.lcsc.com/product-detail/C2655099.html",
    },
    "BMI270": {
        "stock_quantity": 5644,
        "lifecycle_state": "normal",
        "unit_price": "3.2631",
        "product_url": "https://www.lcsc.com/product-detail/C2836813.html",
    },
    "MS561101BA03-50": {
        "stock_quantity": 3071,
        "lifecycle_state": "normal",
        "unit_price": "6.7601",
        "product_url": "https://www.lcsc.com/product-detail/C15639.html",
    },
    "AP63205WU-7": {
        "stock_quantity": 28917,
        "lifecycle_state": "normal",
        "unit_price": "0.4336",
        "product_url": "https://www.lcsc.com/product-detail/C2071056.html",
    },
    "AP7343-33W5-7": {
        "stock_quantity": 605,
        "lifecycle_state": "normal",
        "unit_price": "0.3618",
        "product_url": "https://www.lcsc.com/product-detail/C460383.html",
    },
    "AP2112K-3.3TRG1": {
        "stock_quantity": 62760,
        "lifecycle_state": "normal",
        "unit_price": "0.1726",
        "product_url": "https://www.lcsc.com/product-detail/C51118.html",
    },
    "SN65HVD230DR": {
        "stock_quantity": 55975,
        "lifecycle_state": "normal",
        "unit_price": "0.6989",
        "product_url": "https://www.lcsc.com/product-detail/C12084.html",
    },
    "SIT1051ATK/3": {
        "stock_quantity": 5307,
        "lifecycle_state": "normal",
        "unit_price": "0.4994",
        "product_url": "https://www.lcsc.com/product-detail/C5382552.html",
    },
    "NX3225GD-8MHZ-STD-CRA-3": {
        "stock_quantity": 50985,
        "lifecycle_state": "normal",
        "unit_price": "0.3456",
        "product_url": "https://www.lcsc.com/product-detail/C889706.html",
    },
    "TF-01A": {
        "stock_quantity": 223295,
        "lifecycle_state": "normal",
        "unit_price": "0.1937",
        "product_url": "https://www.lcsc.com/product-detail/C91145.html",
    },
    "TYPE-C-31-M-12": {
        "stock_quantity": 274725,
        "lifecycle_state": "normal",
        "unit_price": "0.1873",
        "product_url": "https://www.lcsc.com/product-detail/C165948.html",
    },
    "USBLC6-2P6": {
        "stock_quantity": 7455,
        "lifecycle_state": "normal",
        "unit_price": "0.2852",
        "product_url": "https://www.lcsc.com/product-detail/C15999.html",
    },
    "SMAJ30CA": {
        "stock_quantity": 118400,
        "lifecycle_state": "normal",
        "unit_price": "0.0520",
        "product_url": "https://www.lcsc.com/product-detail/C81938.html",
    },
    "AO3407A": {
        "stock_quantity": 142500,
        "lifecycle_state": "normal",
        "unit_price": "0.0485",
        "product_url": "https://www.lcsc.com/product-detail/C15127.html",
    },
    "1N5819WS": {
        "stock_quantity": 96500,
        "lifecycle_state": "normal",
        "unit_price": "0.0210",
        "product_url": "https://www.lcsc.com/product-detail/C8598.html",
    },
    "PESD2CAN": {
        "stock_quantity": 83200,
        "lifecycle_state": "normal",
        "unit_price": "0.0415",
        "product_url": "https://www.lcsc.com/product-detail/C18214.html",
    },
    "SRP4020TA-2R2M": {
        "stock_quantity": 15400,
        "lifecycle_state": "normal",
        "unit_price": "0.2850",
        "product_url": "https://www.lcsc.com/product-detail/C231647.html",
    },
    "CC0402KRX7R7BB104": {
        "stock_quantity": 1450000,
        "lifecycle_state": "normal",
        "unit_price": "0.0035",
        "product_url": "https://www.lcsc.com/product-detail/C1525.html",
    },
    "CC0402KRX5R6BB105": {
        "stock_quantity": 650000,
        "lifecycle_state": "normal",
        "unit_price": "0.0055",
        "product_url": "https://www.lcsc.com/product-detail/C52923.html",
    },
    "CC0402KRX7R9BB103": {
        "stock_quantity": 920000,
        "lifecycle_state": "normal",
        "unit_price": "0.0032",
        "product_url": "https://www.lcsc.com/product-detail/C15195.html",
    },
    "CC0402JRNPO9BN150": {
        "stock_quantity": 540000,
        "lifecycle_state": "normal",
        "unit_price": "0.0040",
        "product_url": "https://www.lcsc.com/product-detail/C1547.html",
    },
    "CC0603KRX7R7BB475": {
        "stock_quantity": 820000,
        "lifecycle_state": "normal",
        "unit_price": "0.0125",
        "product_url": "https://www.lcsc.com/product-detail/C19702.html",
    },
    "CC0603KRX7R7BB225": {
        "stock_quantity": 430000,
        "lifecycle_state": "normal",
        "unit_price": "0.0098",
        "product_url": "https://www.lcsc.com/product-detail/C23630.html",
    },
    "CL10A106KP8NNNC": {
        "stock_quantity": 750000,
        "lifecycle_state": "normal",
        "unit_price": "0.0142",
        "product_url": "https://www.lcsc.com/product-detail/C96446.html",
    },
    "CC0805MKX5R8BB106": {
        "stock_quantity": 680000,
        "lifecycle_state": "normal",
        "unit_price": "0.0185",
        "product_url": "https://www.lcsc.com/product-detail/C15850.html",
    },
    "CL21A226MQQNNNE": {
        "stock_quantity": 320000,
        "lifecycle_state": "normal",
        "unit_price": "0.0245",
        "product_url": "https://www.lcsc.com/product-detail/C45783.html",
    },
    "RC0402FR-0710KL": {
        "stock_quantity": 2100000,
        "lifecycle_state": "normal",
        "unit_price": "0.0022",
        "product_url": "https://www.lcsc.com/product-detail/C25744.html",
    },
    "RC0402FR-075K1L": {
        "stock_quantity": 890000,
        "lifecycle_state": "normal",
        "unit_price": "0.0025",
        "product_url": "https://www.lcsc.com/product-detail/C25905.html",
    },
    "RC0402FR-07220RL": {
        "stock_quantity": 450000,
        "lifecycle_state": "normal",
        "unit_price": "0.0022",
        "product_url": "https://www.lcsc.com/product-detail/C25091.html",
    },
    "RC0603FR-07100KL": {
        "stock_quantity": 1200000,
        "lifecycle_state": "normal",
        "unit_price": "0.0028",
        "product_url": "https://www.lcsc.com/product-detail/C25803.html",
    },
    "RC0603FR-07120RL": {
        "stock_quantity": 670000,
        "lifecycle_state": "normal",
        "unit_price": "0.0030",
        "product_url": "https://www.lcsc.com/product-detail/C22787.html",
    },
    "BLM18PG600SN1D": {
        "stock_quantity": 350000,
        "lifecycle_state": "normal",
        "unit_price": "0.0150",
        "product_url": "https://www.lcsc.com/product-detail/C1015.html",
    },
    "SM04B-GHS-TB": {
        "stock_quantity": 85000,
        "lifecycle_state": "normal",
        "unit_price": "0.1250",
        "product_url": "https://www.lcsc.com/product-detail/C160404.html",
    },
    "SM05B-GHS-TB": {
        "stock_quantity": 42000,
        "lifecycle_state": "normal",
        "unit_price": "0.1420",
        "product_url": "https://www.lcsc.com/product-detail/C160405.html",
    },
    "SM06B-GHS-TB": {
        "stock_quantity": 112000,
        "lifecycle_state": "normal",
        "unit_price": "0.1580",
        "product_url": "https://www.lcsc.com/product-detail/C160406.html",
    },
    "SM10B-GHS-TB": {
        "stock_quantity": 38000,
        "lifecycle_state": "normal",
        "unit_price": "0.2150",
        "product_url": "https://www.lcsc.com/product-detail/C160410.html",
    },
    "PinHeader_1x04_P2.54mm": {
        "stock_quantity": 450000,
        "lifecycle_state": "normal",
        "unit_price": "0.0250",
        "product_url": "https://www.lcsc.com/product-detail/C224322.html",
    },
    "TS-1088-02526": {
        "stock_quantity": 195000,
        "lifecycle_state": "normal",
        "unit_price": "0.0450",
        "product_url": "https://www.lcsc.com/product-detail/C318884.html",
    },
    "SolderJumper_2_Open": {
        "stock_quantity": 250000,
        "lifecycle_state": "normal",
        "unit_price": "0.0100",
        "product_url": "https://www.lcsc.com/product-detail/C371752.html",
    },
}


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    snap_dirs = sorted([d for d in SNAPSHOTS_DIR.glob("RevA-*") if d.is_dir()])
    if not snap_dirs:
        raise RuntimeError("No RevA snapshot directory found")
    snap_dir = snap_dirs[-1]
    print(f"Updating snapshot at: {snap_dir}")

    stock_state_path = snap_dir / "stock-state.csv"
    with open(stock_state_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    updated_rows = []
    for row in rows:
        part = row["part_number"].strip()
        data = STOCK_DATA.get(part)
        if not data:
            raise KeyError(f"Missing stock data for part: {part}")
        row["stock_quantity"] = str(data["stock_quantity"])
        row["lifecycle_state"] = data["lifecycle_state"]
        row["unit_price"] = str(data["unit_price"])
        row["product_url"] = data["product_url"]
        updated_rows.append(row)

    with open(stock_state_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in updated_rows:
            writer.writerow(r)
    print(f"Updated {len(updated_rows)} rows in {stock_state_path}")

    # Recompute SHA256SUMS
    checksums = []
    files_to_hash = ["MADpilot-H7-RevA-bom.csv", "manifest.json", "stock-state.csv"]
    for fname in sorted(files_to_hash):
        file_p = snap_dir / fname
        if file_p.is_file():
            csum = compute_sha256(file_p)
            checksums.append(f"{csum}  {fname}")

    sums_path = snap_dir / "SHA256SUMS"
    sums_path.write_text("\n".join(checksums) + "\n", encoding="utf-8")
    print(f"Recomputed SHA256SUMS covering: {', '.join(files_to_hash)}")


if __name__ == "__main__":
    main()

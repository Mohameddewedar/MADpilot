import csv
import datetime
import hashlib
import json
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
BOM_DIR = REPO_ROOT / "hardware" / "bom"
SNAPSHOTS_DIR = BOM_DIR / "snapshots"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestBomSnapshot(unittest.TestCase):
    def setUp(self):
        self.bom_csv = BOM_DIR / "MADpilot-H7-RevA-bom.csv"
        # Find RevA snapshot directory
        self.snapshot_dirs = sorted(
            [d for d in SNAPSHOTS_DIR.glob("RevA-*") if d.is_dir()]
        )

    def test_rev_a_bom_csv_exists_and_valid(self):
        """MADpilot-H7-RevA-bom.csv must exist and contain extracted schematic BOM."""
        self.assertTrue(self.bom_csv.is_file(), f"BOM file missing at {self.bom_csv}")

        with open(self.bom_csv, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertGreater(len(rows), 0, "BOM CSV must have at least one line item")
        self.assertIn("part_number", reader.fieldnames, "BOM CSV must contain 'part_number'")
        self.assertIn("description", reader.fieldnames, "BOM CSV must contain 'description'")

        # Verify key critical components from 7 schematic sheets are in BOM
        key_critical = [
            "STM32H743IIT6",
            "ICM-42605",
            "BMI270",
            "MS561101BA03-50",
            "AP63205WU-7",
            "AP7343-33W5-7",
            "AP2112K-3.3TRG1",
            "SN65HVD230DR",
            "SIT1051ATK/3",
            "NX3225GD-8MHZ-STD-CRA-3",
            "TF-01A",
            "TYPE-C-31-M-12",
            "USBLC6-2P6",
        ]
        all_part_text = " ".join(r["part_number"] for r in rows)
        for comp in key_critical:
            self.assertIn(comp, all_part_text, f"Key component {comp} missing from BOM CSV")

        # Verify total component count accounts for all 107 schematic instances
        if "quantity" in reader.fieldnames:
            total_qty = sum(int(r["quantity"]) for r in rows if r.get("quantity"))
            self.assertEqual(total_qty, 107, f"Expected total quantity 107 across 7 sheets, got {total_qty}")

    def test_snapshot_directory_structure(self):
        """Snapshot directory under hardware/bom/snapshots/RevA-<date>/ must contain required files."""
        self.assertTrue(
            len(self.snapshot_dirs) > 0,
            f"No RevA snapshot directory found under {SNAPSHOTS_DIR}",
        )
        snap_dir = self.snapshot_dirs[-1]

        expected_files = [
            snap_dir / "MADpilot-H7-RevA-bom.csv",
            snap_dir / "stock-state.csv",
            snap_dir / "manifest.json",
            snap_dir / "SHA256SUMS",
        ]
        for ef in expected_files:
            self.assertTrue(ef.is_file(), f"Snapshot artifact missing: {ef}")

    def test_stock_state_procurement_data_complete(self):
        """Every entry in stock-state.csv must have positive stock, valid lifecycle, price, and URL."""
        self.assertTrue(len(self.snapshot_dirs) > 0, "No RevA snapshot directory found")
        snap_dir = self.snapshot_dirs[-1]
        stock_state_path = snap_dir / "stock-state.csv"
        self.assertTrue(stock_state_path.is_file(), f"Missing {stock_state_path}")

        with open(stock_state_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertGreater(len(rows), 0, "stock-state.csv must contain data rows")
        expected_cols = [
            "part_number",
            "description",
            "stock_quantity",
            "lifecycle_state",
            "unit_price",
            "product_url",
        ]
        for col in expected_cols:
            self.assertIn(col, reader.fieldnames, f"Missing column '{col}' in stock-state.csv")

        for idx, row in enumerate(rows):
            part = row.get("part_number", "").strip()
            self.assertTrue(part, f"Row {idx} has empty part_number")

            # Stock quantity > 0
            stock_str = row.get("stock_quantity", "").strip()
            self.assertTrue(stock_str, f"Row {idx} ({part}) has empty stock_quantity")
            stock = int(stock_str)
            self.assertGreater(stock, 0, f"Stock quantity for {part} must be > 0, got {stock}")

            # Lifecycle state active/normal
            lifecycle = row.get("lifecycle_state", "").strip().lower()
            self.assertIn(
                lifecycle,
                ["active", "normal"],
                f"Lifecycle for {part} must be active or normal, got '{lifecycle}'",
            )

            # Unit price > 0
            price_str = row.get("unit_price", "").strip().replace("$", "")
            self.assertTrue(price_str, f"Row {idx} ({part}) has empty unit_price")
            price = float(price_str)
            self.assertGreater(price, 0.0, f"Unit price for {part} must be > 0, got {price}")

            # Product URL starting with https://
            url = row.get("product_url", "").strip()
            self.assertTrue(
                url.startswith("https://"),
                f"Product URL for {part} must start with https://, got '{url}'",
            )

    def test_cryptographic_checksums_match(self):
        """All files listed in SHA256SUMS must match their computed checksums exactly."""
        self.assertTrue(len(self.snapshot_dirs) > 0, "No RevA snapshot directory found")
        snap_dir = self.snapshot_dirs[-1]
        sums_file = snap_dir / "SHA256SUMS"
        self.assertTrue(sums_file.is_file(), f"Missing SHA256SUMS at {sums_file}")

        lines = [
            line.strip()
            for line in sums_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        self.assertGreater(len(lines), 0, "SHA256SUMS must contain checksum entries")

        checked_files = set()
        for line in lines:
            parts = line.split(maxsplit=1)
            self.assertEqual(len(parts), 2, f"Malformed SHA256SUMS line: '{line}'")
            expected_hash, fname = parts[0], parts[1].strip()
            target_path = snap_dir / fname
            self.assertTrue(target_path.is_file(), f"File in SHA256SUMS does not exist: {target_path}")

            actual_hash = compute_sha256(target_path)
            self.assertEqual(
                actual_hash,
                expected_hash,
                f"Checksum mismatch for {fname}: expected {expected_hash}, got {actual_hash}",
            )
            checked_files.add(fname)

        # Must at least cover the BOM, stock-state.csv, and manifest.json
        expected_snap_files = {"MADpilot-H7-RevA-bom.csv", "stock-state.csv", "manifest.json"}
        self.assertTrue(
            expected_snap_files.issubset(checked_files),
            f"SHA256SUMS did not cover all required files: {expected_snap_files - checked_files}",
        )

    def test_manifest_metadata(self):
        """manifest.json must contain revision: 'RevA', valid snapshot_date, and matching part_count."""
        self.assertTrue(len(self.snapshot_dirs) > 0, "No RevA snapshot directory found")
        snap_dir = self.snapshot_dirs[-1]
        manifest_file = snap_dir / "manifest.json"
        self.assertTrue(manifest_file.is_file(), f"Missing manifest.json at {manifest_file}")

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest.get("revision"), "RevA", "Manifest revision must be 'RevA'")
        date_str = manifest.get("snapshot_date", "")
        # Validate date parseable
        parsed_date = datetime.date.fromisoformat(date_str)
        self.assertIsNotNone(parsed_date)

        # Validate part_count matches lines in stock-state.csv and BOM
        part_count = manifest.get("part_count")
        self.assertIsInstance(part_count, int)
        self.assertGreater(part_count, 0)

        stock_state_path = snap_dir / "stock-state.csv"
        with open(stock_state_path, "r", encoding="utf-8-sig") as f:
            stock_rows = [row for row in csv.reader(f) if any(c.strip() for c in row)][1:]
        self.assertEqual(
            part_count,
            len(stock_rows),
            f"Manifest part_count ({part_count}) != stock-state rows ({len(stock_rows)})",
        )


if __name__ == "__main__":
    unittest.main()

import csv
import re
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
BOM_PATH = REPO_ROOT / "hardware" / "bom" / "MADpilot-H7-RevA-bom.csv"

# Critical Rev A parts: part_number -> exact LCSC number (tool-agnostic BOM invariants)
CRITICAL_PARTS_LCSC = {
    "STM32H743IIT6": "C89597",
    "ICM-42605": "C2655099",
    "BMI270": "C2836813",
    "MS561101BA03-50": "C15639",
    "AP63205WU-7": "C2071056",
    "AP7343-33W5-7": "C460383",
    "AP2112K-3.3TRG1": "C51118",
    "SN65HVD230DR": "C12084",
    "SIT1051ATK/3": "C5382552",
    "NX3225GD-8MHZ-STD-CRA-3": "C889706",
    "TF-01A": "C91145",
    "TYPE-C-31-M-12": "C165948",
    "USBLC6-2P6": "C15999",
    "SMAJ30CA": "C81938",
    "AO3407A": "C15127",
    "1N5819WS": "C8598",
    "PESD2CAN": "C18214",
    "SRP4020TA-2R2M": "C231647",
}

# part_number -> minimum instance count inherited from the retired schematic tests
MIN_QUANTITIES = {
    "CC0402KRX7R7BB104": 8,
    "CC0402KRX5R6BB105": 1,
    "CC0402KRX7R9BB103": 1,
    "CC0402JRNPO9BN150": 2,
    "CC0603KRX7R7BB225": 2,
    "RC0402FR-0710KL": 5,
    "RC0402FR-075K1L": 2,
    "RC0603FR-07120RL": 2,
    "1N5819WS": 2,
    "PESD2CAN": 2,
    "SolderJumper_2_Open": 2,
}

PROHIBITED_MAGNETOMETERS = ["QMC5883", "HMC5883", "IST8310", "LIS3MDL", "MMC5983"]

REQUIRED_SHEET_REFS = ["POWER:", "MCU:", "SENSORS:", "CAN:", "STORAGE:", "CONNECTORS:", "DEBUG:"]


def load_bom_rows():
    with open(BOM_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def load_stock_state_rows():
    csv_path = REPO_ROOT / "hardware" / "bom" / "critical-stock-state.csv"
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader), csv_path


class TestRevABomRequirements(unittest.TestCase):
    """Rev A design invariants validated against the frozen EDA BOM CSV (Altium-compatible)."""

    def test_rev_a_bom_exists_with_required_columns(self):
        """MADpilot-H7-RevA-bom.csv must exist with part_number, description, lcsc_part, quantity."""
        self.assertTrue(BOM_PATH.is_file(), f"Missing Rev A BOM at {BOM_PATH}")
        fieldnames, rows = load_bom_rows()
        for col in ("part_number", "description", "lcsc_part", "quantity"):
            self.assertIn(col, fieldnames, f"BOM must contain column '{col}'")
        self.assertGreater(len(rows), 0, "BOM must contain at least one line item")

    def test_critical_parts_present_with_matching_lcsc(self):
        """Every critical Rev A part must appear with its exact LCSC number."""
        fieldnames, rows = load_bom_rows()
        by_part = {r["part_number"].strip(): r for r in rows}
        for part, lcsc in CRITICAL_PARTS_LCSC.items():
            self.assertIn(part, by_part, f"Critical part {part} missing from Rev A BOM")
            self.assertEqual(
                by_part[part]["lcsc_part"].strip(),
                lcsc,
                f"{part} LCSC must be {lcsc}",
            )

    def test_minimum_quantities(self):
        """Instance-count minimums inherited from the retired schematic tests."""
        fieldnames, rows = load_bom_rows()
        by_part = {r["part_number"].strip(): r for r in rows}
        for part, min_qty in MIN_QUANTITIES.items():
            qty = int(by_part[part]["quantity"].strip())
            self.assertGreaterEqual(qty, min_qty, f"{part} must have >= {min_qty} instances, got {qty}")

    def test_total_instance_count(self):
        """Rev A design totals 107 component instances across the 7 sheets."""
        fieldnames, rows = load_bom_rows()
        total = sum(int(r["quantity"].strip()) for r in rows if r.get("quantity"))
        self.assertEqual(total, 107, f"Expected 107 Rev A instances, got {total}")

    def test_all_seven_sheets_represented(self):
        """BOM references must cover POWER, MCU, SENSORS, CAN, STORAGE, CONNECTORS, DEBUG."""
        fieldnames, rows = load_bom_rows()
        all_refs = " ".join(r.get("references", "") for r in rows)
        for sheet in REQUIRED_SHEET_REFS:
            self.assertIn(sheet, all_refs, f"Sheet prefix '{sheet}' missing from BOM references")

    def test_mcu_footprint_is_lqfp176(self):
        """STM32H743IIT6 row must carry an LQFP-176 footprint."""
        fieldnames, rows = load_bom_rows()
        mcu = next(r for r in rows if r["part_number"].strip() == "STM32H743IIT6")
        self.assertIn("LQFP-176", mcu.get("footprint", ""), "MCU footprint must be LQFP-176")

    def test_no_onboard_magnetometer(self):
        """No magnetometer may appear in the Rev A BOM (external GNSS-puck compass only)."""
        fieldnames, rows = load_bom_rows()
        for r in rows:
            text = (r["part_number"] + " " + r["description"]).upper()
            for mag in PROHIBITED_MAGNETOMETERS:
                self.assertNotIn(mag, text, f"Prohibited magnetometer '{mag}' found in Rev A BOM")


class TestCriticalStockState(unittest.TestCase):
    """In-Stock-First criteria on hardware/bom/critical-stock-state.csv."""

    def test_critical_stock_state_exists_and_valid(self):
        """Verify the critical parts stock state CSV exists and satisfies In-Stock-First criteria."""
        fieldnames, rows, csv_path = load_stock_state_rows()
        self.assertTrue(csv_path.is_file(), f"Missing critical stock state CSV at {csv_path}")

        expected_fields = ["part_number", "description", "lcsc_part", "stock_quantity", "lifecycle_state", "unit_price", "product_url"]
        for field in expected_fields:
            self.assertIn(field, fieldnames, f"Missing column {field} in {csv_path}")

        self.assertGreaterEqual(len(rows), 12, f"Expected at least 12 critical components, got {len(rows)}")

        required_parts = [
            "STM32H743IIT6",
            "ICM-42605",
            "BMI270",
            "MS5611",
            "AP63205",
            "AP7343",
            "AP2112K",
            "SN65HVD230",
            "8MHZ",
            "TF-01A",
            "TYPE-C-31-M-12",
            "USBLC6-2P6",
        ]
        for req in required_parts:
            found = any(req.lower() in (r["part_number"] + " " + r["description"]).lower() for r in rows)
            self.assertTrue(found, f"Required component {req} not found in {csv_path}")

        for row in rows:
            lcsc = row["lcsc_part"].strip()
            self.assertTrue(re.match(r"^C\d+$", lcsc), f"Invalid LCSC part number: {lcsc}")
            stock = int(row["stock_quantity"].strip())
            self.assertGreater(stock, 0, f"Stock quantity for {row['part_number']} must be > 0, got {stock}")
            lifecycle = row["lifecycle_state"].strip().lower()
            self.assertIn(lifecycle, ["normal", "active"], f"Lifecycle for {row['part_number']} must be active/normal, got {lifecycle}")
            price = float(row["unit_price"].strip().replace("$", ""))
            self.assertGreater(price, 0.0, f"Unit price for {row['part_number']} must be > 0")
            url = row["product_url"].strip()
            self.assertTrue(url.startswith("https://"), f"Product URL must start with https://, got {url}")


class TestAttribution(unittest.TestCase):
    """Open-hardware attribution obligations (CERN-OHL-S-2.0 / LEVIA-H7)."""

    def test_hardware_readme_attribution(self):
        """Verify hardware/MADpilot-H7/README.md has formal CERN-OHL-S-2.0 attribution for LEVIA-H7."""
        readme_file = REPO_ROOT / "hardware" / "MADpilot-H7" / "README.md"
        self.assertTrue(readme_file.is_file(), f"Missing hardware README at {readme_file}")

        content = readme_file.read_text(encoding="utf-8")
        self.assertIn("CERN-OHL-S-2.0", content)
        self.assertIn("LEVIA-H7", content)
        self.assertIn("piecol", content)

    def test_root_license_hardware_attribution(self):
        """Verify root LICENSE includes hardware attribution citing LEVIA-H7 and CERN-OHL-S-2.0."""
        license_file = REPO_ROOT / "LICENSE"
        self.assertTrue(license_file.is_file())

        content = license_file.read_text(encoding="utf-8")
        self.assertIn("CERN-OHL-S-2.0", content)
        self.assertIn("LEVIA-H7", content)
        self.assertIn("piecol", content)


if __name__ == "__main__":
    unittest.main()

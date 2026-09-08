import csv
import json
import re
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent

class TestIssue11Deliverables(unittest.TestCase):
    def test_critical_stock_state_exists_and_valid(self):
        """Verify the critical parts stock state CSV exists and satisfies In-Stock-First criteria."""
        csv_path = REPO_ROOT / "hardware" / "bom" / "critical-stock-state.csv"
        self.assertTrue(csv_path.is_file(), f"Missing critical stock state CSV at {csv_path}")

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        expected_fields = ["part_number", "description", "lcsc_part", "stock_quantity", "lifecycle_state", "unit_price", "product_url"]
        for field in expected_fields:
            self.assertIn(field, reader.fieldnames, f"Missing column {field} in {csv_path}")

        # At least 12 critical parts
        self.assertGreaterEqual(len(rows), 12, f"Expected at least 12 critical components, got {len(rows)}")

        # Verify key parts are present
        required_parts = [
            "STM32H743IIT6",
            "ICM-42605",
            "BMI270",
            "MS5611",
            "AP63205",      # 5V buck
            "AP7343",       # 3V3_SENS LDO
            "AP2112K",      # 3V3_MCU LDO
            "SN65HVD230",   # CAN transceiver
            "8MHZ",         # 8 MHz crystal / resonator
            "TF-01A",       # MicroSD slot
            "TYPE-C-31-M-12", # USB-C receptacle
            "USBLC6-2P6",   # USB ESD protection
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

    def test_kicad_project_skeleton_exists(self):
        """Verify the KiCad project skeleton directory and files exist with valid formats."""
        hw_dir = REPO_ROOT / "hardware" / "MADpilot-H7"
        self.assertTrue(hw_dir.is_dir(), f"Missing hardware directory at {hw_dir}")

        pro_file = hw_dir / "MADpilot-H7.kicad_pro"
        self.assertTrue(pro_file.is_file(), f"Missing KiCad project file at {pro_file}")

        # Must be valid JSON
        with open(pro_file, "r", encoding="utf-8") as f:
            pro_data = json.load(f)
        self.assertIsInstance(pro_data, dict)
        self.assertIn("meta", pro_data)

        sch_file = hw_dir / "MADpilot-H7.kicad_sch"
        self.assertTrue(sch_file.is_file(), f"Missing KiCad schematic file at {sch_file}")

        # Must be valid S-expression syntax
        content = sch_file.read_text(encoding="utf-8")
        self.assertTrue(content.strip().startswith("(kicad_sch"), "Schematic must start with (kicad_sch")
        self.assertTrue(content.strip().endswith(")"), "Schematic must end with closing parenthesis")
        self.assertIn("MADpilot-H7", content)

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

import re
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
HW_DIR = REPO_ROOT / "hardware" / "MADpilot-H7"

def extract_symbols(content: str):
    """Extract symbol instances and their properties from a .kicad_sch text."""
    symbols = []
    sym_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"([^"]+)"\)(.*?)\n\s*\)', content, re.DOTALL)
    for m in sym_matches:
        lib_id = m.group(1)
        body = m.group(2)
        props = dict(re.findall(r'\(property\s+"([^"]+)"\s+"([^"]*)"', body))
        props["_lib_id"] = lib_id
        props["_raw"] = body
        symbols.append(props)
    return symbols

def extract_labels(content: str):
    """Extract all label names from schematic."""
    labels = re.findall(r'\((?:hierarchical_label|global_label|label)\s+"([^"]+)"', content)
    return set(labels)


class TestSensorsSchematic(unittest.TestCase):
    def setUp(self):
        self.sensors_file = HW_DIR / "SENSORS.kicad_sch"

    def test_sensors_schematic_exists_and_valid_sexp(self):
        """SENSORS.kicad_sch must exist and be valid KiCad S-expression."""
        self.assertTrue(self.sensors_file.is_file(), f"Missing {self.sensors_file}")
        content = self.sensors_file.read_text(encoding="utf-8")
        self.assertTrue(content.strip().startswith("(kicad_sch"), "Must begin with (kicad_sch")
        self.assertTrue(content.strip().endswith(")"), "Must end with ')'")
        open_count = content.count('(')
        close_count = content.count(')')
        self.assertEqual(open_count, close_count, f"Parenthesis mismatch: {open_count} open vs {close_count} close")

    def test_icm42605_primary_imu_present_and_wired(self):
        """SENSORS.kicad_sch must capture primary IMU ICM-42605 (LCSC C2655099) on SPI1."""
        self.assertTrue(self.sensors_file.is_file())
        content = self.sensors_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        icm_syms = [s for s in symbols if "ICM-42605" in s.get("Value", "") or "ICM-42605" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(icm_syms), 1, "ICM-42605 primary IMU symbol not found")
        icm = icm_syms[0]
        self.assertEqual(icm.get("LCSC", ""), "C2655099", "ICM-42605 LCSC part number must match critical BOM (C2655099)")
        self.assertIn("LGA-14", icm.get("Footprint", ""), "Footprint should specify LGA-14")

        # Verify SPI1 net labels
        labels = extract_labels(content)
        expected_spi1 = {"IMU1_SCK", "IMU1_MISO", "IMU1_MOSI", "IMU1_CS", "IMU1_DRDY"}
        self.assertTrue(expected_spi1.issubset(labels), f"Missing SPI1 nets in SENSORS: {expected_spi1 - labels}")

    def test_bmi270_secondary_imu_present_and_wired(self):
        """SENSORS.kicad_sch must capture secondary IMU BMI270 (LCSC C2836813) on SPI4."""
        self.assertTrue(self.sensors_file.is_file())
        content = self.sensors_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        bmi_syms = [s for s in symbols if "BMI270" in s.get("Value", "") or "BMI270" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(bmi_syms), 1, "BMI270 secondary IMU symbol not found")
        bmi = bmi_syms[0]
        self.assertEqual(bmi.get("LCSC", ""), "C2836813", "BMI270 LCSC part number must match critical BOM (C2836813)")
        self.assertIn("LGA-14", bmi.get("Footprint", ""), "Footprint should specify LGA-14")

        # Verify SPI4 net labels
        labels = extract_labels(content)
        expected_spi4 = {"IMU2_SCK", "IMU2_MISO", "IMU2_MOSI", "IMU2_CS", "IMU2_DRDY"}
        self.assertTrue(expected_spi4.issubset(labels), f"Missing SPI4 nets in SENSORS: {expected_spi4 - labels}")

    def test_ms5611_barometer_present_and_wired(self):
        """SENSORS.kicad_sch must capture MS561101BA03-50 barometer (LCSC C15639) on I2C2."""
        self.assertTrue(self.sensors_file.is_file())
        content = self.sensors_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        baro_syms = [s for s in symbols if "MS5611" in s.get("Value", "") or "MS5611" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(baro_syms), 1, "MS5611 barometer symbol not found")
        baro = baro_syms[0]
        self.assertEqual(baro.get("LCSC", ""), "C15639", "MS5611 LCSC part number must match critical BOM (C15639)")

        # Verify I2C2 net labels
        labels = extract_labels(content)
        expected_i2c = {"BARO_SCL", "BARO_SDA"}
        self.assertTrue(expected_i2c.issubset(labels), f"Missing I2C2 nets in SENSORS: {expected_i2c - labels}")

    def test_sensors_power_and_decoupling(self):
        """SENSORS.kicad_sch components must be powered from 3V3_SENS with decoupling capacitors."""
        self.assertTrue(self.sensors_file.is_file())
        content = self.sensors_file.read_text(encoding="utf-8")
        labels = extract_labels(content)
        self.assertIn("3V3_SENS", labels, "3V3_SENS power rail missing from SENSORS sheet")
        self.assertIn("GND", labels, "GND missing from SENSORS sheet")

        # Check decoupling capacitors: at least 4 (VDD + VDDIO for ICM, VDD + VDDIO for BMI, VDD for MS5611)
        symbols = extract_symbols(content)
        caps = [s for s in symbols if s.get("Reference", "").startswith("C")]
        self.assertGreaterEqual(len(caps), 4, f"Expected at least 4 decoupling capacitors in SENSORS, found {len(caps)}")

    def test_strictly_no_magnetometer_onboard(self):
        """No magnetometer (QMC5883, HMC5883, IST8310, LIS3MDL, etc.) in SENSORS.kicad_sch."""
        self.assertTrue(self.sensors_file.is_file())
        content = self.sensors_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        
        prohibited_mag_names = ["QMC5883", "HMC5883", "IST8310", "LIS3MDL", "MMC5983", "MAG"]
        for sym in symbols:
            val = sym.get("Value", "").upper()
            lib_id = sym.get("_lib_id", "").upper()
            for mag in prohibited_mag_names:
                self.assertNotIn(mag, val, f"Prohibited magnetometer found in Value: {val}")
                self.assertNotIn(mag, lib_id, f"Prohibited magnetometer found in lib_id: {lib_id}")


class TestCANSchematic(unittest.TestCase):
    def setUp(self):
        self.can_file = HW_DIR / "CAN.kicad_sch"

    def test_can_schematic_exists_and_valid_sexp(self):
        """CAN.kicad_sch must exist and be valid KiCad S-expression."""
        self.assertTrue(self.can_file.is_file(), f"Missing {self.can_file}")
        content = self.can_file.read_text(encoding="utf-8")
        self.assertTrue(content.strip().startswith("(kicad_sch"), "Must begin with (kicad_sch")
        self.assertTrue(content.strip().endswith(")"), "Must end with ')'")
        open_count = content.count('(')
        close_count = content.count(')')
        self.assertEqual(open_count, close_count, f"Parenthesis mismatch: {open_count} open vs {close_count} close")

    def test_dual_transceivers_present(self):
        """CAN.kicad_sch must have CAN1 SN65HVD230DR (C12084) and CAN2 SIT1051ATK/3 (C5382552)."""
        self.assertTrue(self.can_file.is_file())
        content = self.can_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)

        # CAN1: SN65HVD230DR
        can1_syms = [s for s in symbols if "SN65HVD230" in s.get("Value", "") or "SN65HVD230" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(can1_syms), 1, "SN65HVD230DR CAN1 transceiver symbol not found")
        self.assertEqual(can1_syms[0].get("LCSC", ""), "C12084", "SN65HVD230DR LCSC part must match BOM (C12084)")

        # CAN2: SIT1051ATK/3
        can2_syms = [s for s in symbols if "SIT1051" in s.get("Value", "") or "SIT1051" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(can2_syms), 1, "SIT1051ATK/3 CAN2 transceiver symbol not found")
        self.assertEqual(can2_syms[0].get("LCSC", ""), "C5382552", "SIT1051ATK/3 LCSC part must match BOM (C5382552)")

        # Verify MCU connection nets
        labels = extract_labels(content)
        expected_can_nets = {"FDCAN1_TX", "FDCAN1_RX", "FDCAN2_TX", "FDCAN2_RX"}
        self.assertTrue(expected_can_nets.issubset(labels), f"Missing CAN MCU nets: {expected_can_nets - labels}")

    def test_can_bus_termination_resistors_and_jumpers(self):
        """CAN.kicad_sch must have 120-ohm termination resistor and switch/jumper for each CAN bus."""
        self.assertTrue(self.can_file.is_file())
        content = self.can_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)

        # 120 ohm resistors
        r_120 = [s for s in symbols if s.get("Reference", "").startswith("R") and "120" in s.get("Value", "")]
        self.assertGreaterEqual(len(r_120), 2, f"Expected 2x 120-ohm termination resistors, found {len(r_120)}")

        # Jumpers / switches for termination
        jumpers = [s for s in symbols if s.get("Reference", "").startswith("JP") or "Jumper" in s.get("_lib_id", "") or "Jumper" in s.get("Value", "")]
        self.assertGreaterEqual(len(jumpers), 2, f"Expected 2x termination jumpers/switches, found {len(jumpers)}")

    def test_can_esd_protection(self):
        """CAN.kicad_sch must include PESD2CAN / TVS protection diodes on CAN differential lines."""
        self.assertTrue(self.can_file.is_file())
        content = self.can_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)

        esd_syms = [s for s in symbols if "PESD2CAN" in s.get("Value", "") or "PESD2CAN" in s.get("_lib_id", "") or "TVS" in s.get("_lib_id", "") or "TVS" in s.get("Value", "")]
        self.assertGreaterEqual(len(esd_syms), 2, f"Expected at least 2 ESD protection diode arrays for CAN1 and CAN2, found {len(esd_syms)}")

    def test_can_connectors_and_bus_lines(self):
        """CAN.kicad_sch must feature CAN1 and CAN2 connectors and differential lines CAN_H / CAN_L."""
        self.assertTrue(self.can_file.is_file())
        content = self.can_file.read_text(encoding="utf-8")
        labels = extract_labels(content)

        expected_bus_lines = {"CAN1_H", "CAN1_L", "CAN2_H", "CAN2_L"}
        self.assertTrue(expected_bus_lines.issubset(labels), f"Missing CAN bus differential lines: {expected_bus_lines - labels}")

        symbols = extract_symbols(content)
        connectors = [s for s in symbols if s.get("Reference", "").startswith("J")]
        self.assertGreaterEqual(len(connectors), 2, f"Expected at least 2 CAN bus connectors (JST-GH), found {len(connectors)}")


class TestRootSchematicSensorsAndCAN(unittest.TestCase):
    def setUp(self):
        self.root_file = HW_DIR / "MADpilot-H7.kicad_sch"

    def test_root_instantiates_sensors_and_can_sheets(self):
        """MADpilot-H7.kicad_sch must instantiate SENSORS and CAN hierarchical sheets."""
        self.assertTrue(self.root_file.is_file(), f"Missing {self.root_file}")
        content = self.root_file.read_text(encoding="utf-8")

        # Check sheet references
        self.assertIn("SENSORS.kicad_sch", content, "SENSORS.kicad_sch not referenced in root sheet")
        self.assertIn("CAN.kicad_sch", content, "CAN.kicad_sch not referenced in root sheet")

        # Check sheetnames
        self.assertIn('"Sheetname" "SENSORS"', content)
        self.assertIn('"Sheetname" "CAN"', content)

        # Check page instances (Root, POWER, MCU, SENSORS, CAN = at least 5)
        sheet_inst_match = re.findall(r'\(path\s+"/[^"]*"\s+\(page\s+"([0-9]+)"\)\s*\)', content)
        self.assertGreaterEqual(len(sheet_inst_match), 5, "Root sheet must have at least 5 page instances")


if __name__ == "__main__":
    unittest.main()

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


class TestMCUSchematic(unittest.TestCase):
    def setUp(self):
        self.mcu_file = HW_DIR / "MCU.kicad_sch"

    def test_mcu_schematic_exists_and_valid_sexp(self):
        """MCU.kicad_sch must exist and be valid KiCad S-expression."""
        self.assertTrue(self.mcu_file.is_file(), f"Missing {self.mcu_file}")
        content = self.mcu_file.read_text(encoding="utf-8")
        self.assertTrue(content.strip().startswith("(kicad_sch"), "Must begin with (kicad_sch")
        self.assertTrue(content.strip().endswith(")"), "Must end with ')'")
        # Validate balanced parentheses
        open_count = content.count('(')
        close_count = content.count(')')
        self.assertEqual(open_count, close_count, f"Parenthesis mismatch: {open_count} open vs {close_count} close")

    def test_stm32h743iit6_mcu_present(self):
        """MCU.kicad_sch must contain STM32H743IIT6 in LQFP-176 package with LCSC C89597."""
        self.assertTrue(self.mcu_file.is_file())
        content = self.mcu_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        mcu_syms = [s for s in symbols if "STM32H743IIT" in s.get("Value", "") or "STM32H743IIT" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(mcu_syms), 1, "STM32H743IIT6 MCU symbol not found")
        mcu = mcu_syms[0]
        self.assertIn("176", mcu.get("Footprint", ""), "Footprint should specify LQFP-176")
        self.assertEqual(mcu.get("LCSC", ""), "C89597", "LCSC part number must match critical BOM (C89597)")

    def test_vcap_capacitors(self):
        """STM32H743 internal regulator requires dual low-ESR ceramic VCAP capacitors (2.2uF)."""
        self.assertTrue(self.mcu_file.is_file())
        content = self.mcu_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        vcap_caps = [s for s in symbols if "VCAP" in s.get("Reference", "") or "VCAP" in s.get("_raw", "") or "2.2u" in s.get("Value", "")]
        self.assertGreaterEqual(len(vcap_caps), 2, "Expected at least 2 VCAP capacitors (2.2uF each)")

    def test_power_and_decoupling_capacitors(self):
        """Verify decoupling capacitors: 100nF on VDD, and 10nF+1uF on VDDA/VREF+."""
        self.assertTrue(self.mcu_file.is_file())
        content = self.mcu_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        cap_values = [s.get("Value", "") for s in symbols if s.get("Reference", "").startswith("C")]
        
        # 100nF decoupling capacitors (at least 8 for the multiple VDD pins of LQFP-176)
        c_100n = [v for v in cap_values if "100n" in v]
        self.assertGreaterEqual(len(c_100n), 8, f"Expected at least 8x 100nF decoupling caps, found {len(c_100n)}")

        # 10nF and 1uF caps on VDDA/VREF+
        c_10n = [v for v in cap_values if "10n" in v]
        c_1u = [v for v in cap_values if "1u" in v or "1.0u" in v]
        self.assertGreaterEqual(len(c_10n), 1, "Expected at least 1x 10nF cap for VDDA/VREF+")
        self.assertGreaterEqual(len(c_1u), 1, "Expected at least 1x 1uF cap for VDDA/VREF+")

    def test_hse_crystal_circuit(self):
        """8.000 MHz quartz crystal with matching load capacitors on OSC_IN/OSC_OUT."""
        self.assertTrue(self.mcu_file.is_file())
        content = self.mcu_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        crystals = [s for s in symbols if s.get("Reference", "").startswith("Y") or s.get("Reference", "").startswith("X")]
        self.assertGreaterEqual(len(crystals), 1, "Crystal resonator symbol (Y1/X1) not found")
        xtal = crystals[0]
        self.assertTrue("8" in xtal.get("Value", "") or "8MHz" in xtal.get("Value", "") or "8.000" in xtal.get("Value", ""))
        self.assertEqual(xtal.get("LCSC", ""), "C889706", "Crystal LCSC part number must match critical BOM (C889706)")

        labels = extract_labels(content)
        self.assertTrue({"OSC_IN", "OSC_OUT"}.issubset(labels), "Missing OSC_IN / OSC_OUT nets")

    def test_nrst_reset_circuit(self):
        """NRST circuit with pull-up resistor, 100nF filter cap, and reset push button."""
        self.assertTrue(self.mcu_file.is_file())
        content = self.mcu_file.read_text(encoding="utf-8")
        labels = extract_labels(content)
        self.assertIn("NRST", labels, "NRST label missing from MCU sheet")

        symbols = extract_symbols(content)
        switches = [s for s in symbols if s.get("Reference", "").startswith("SW")]
        self.assertGreaterEqual(len(switches), 1, "Pushbutton switch for Reset or Boot not found")

    def test_boot0_circuit(self):
        """BOOT0 circuit with 10k pull-down resistor and button to 3.3V."""
        self.assertTrue(self.mcu_file.is_file())
        content = self.mcu_file.read_text(encoding="utf-8")
        labels = extract_labels(content)
        self.assertIn("BOOT0", labels, "BOOT0 label missing from MCU sheet")

    def test_peripheral_net_labels_match_hwdef(self):
        """Verify MCU net labels adhere to comparative-review.md and hwdef.dat."""
        self.assertTrue(self.mcu_file.is_file())
        content = self.mcu_file.read_text(encoding="utf-8")
        labels = extract_labels(content)

        expected_nets = [
            # Primary IMU (SPI1) & Secondary IMU (SPI4)
            "IMU1_SCK", "IMU1_MISO", "IMU1_MOSI", "IMU1_CS", "IMU1_DRDY",
            "IMU2_SCK", "IMU2_MISO", "IMU2_MOSI", "IMU2_CS", "IMU2_DRDY",
            # Baro (I2C2) & External I2C (I2C1, I2C4)
            "BARO_SCL", "BARO_SDA", "GPS_SCL", "GPS_SDA", "EXT_I2C_SCL", "EXT_I2C_SDA",
            # CAN1 & CAN2
            "FDCAN1_RX", "FDCAN1_TX", "FDCAN2_RX", "FDCAN2_TX",
            # Serial ports
            "GPS1_TX", "GPS1_RX", "GPS2_TX", "GPS2_RX",
            "TELEM1_TX", "TELEM1_RX", "TELEM1_CTS", "TELEM1_RTS",
            "TELEM2_TX", "TELEM2_RX", "TELEM2_CTS", "TELEM2_RTS",
            "RC_TX", "RC_RX",
            # PWM Actuators (12 channels)
            "PWM1", "PWM2", "PWM3", "PWM4", "PWM5", "PWM6",
            "PWM7", "PWM8", "PWM9", "PWM10", "PWM11", "PWM12",
            # ADC1 sensors
            "VOLTAGE1", "CURRENT1", "VOLTAGE2", "CURRENT2", "RSSI_ADC",
            # USB Full-Speed
            "OTG_FS_DM", "OTG_FS_DP", "VBUS_DETECT",
            # MicroSD 4-bit
            "SDMMC1_D0", "SDMMC1_D1", "SDMMC1_D2", "SDMMC1_D3", "SDMMC1_CK", "SDMMC1_CMD",
            # Safety & Alarm
            "SAFETY_SW", "SAFETY_LED", "BUZZER"
        ]

        for net in expected_nets:
            self.assertIn(net, labels, f"Expected net label {net} not found in MCU schematic")


class TestPowerSchematic(unittest.TestCase):
    def setUp(self):
        self.pwr_file = HW_DIR / "POWER.kicad_sch"

    def test_power_schematic_exists_and_valid_sexp(self):
        """POWER.kicad_sch must exist and be valid KiCad S-expression."""
        self.assertTrue(self.pwr_file.is_file(), f"Missing {self.pwr_file}")
        content = self.pwr_file.read_text(encoding="utf-8")
        self.assertTrue(content.strip().startswith("(kicad_sch"), "Must begin with (kicad_sch")
        self.assertTrue(content.strip().endswith(")"), "Must end with ')'")
        open_count = content.count('(')
        close_count = content.count(')')
        self.assertEqual(open_count, close_count, f"Parenthesis mismatch: {open_count} open vs {close_count} close")

    def test_ap63205_buck_converter(self):
        """POWER.kicad_sch must include AP63205 5V 2A synchronous buck with input filtering."""
        self.assertTrue(self.pwr_file.is_file())
        content = self.pwr_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        bucks = [s for s in symbols if "AP63205" in s.get("Value", "") or "AP63205" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(bucks), 1, "AP63205 buck regulator symbol not found")
        buck = bucks[0]
        self.assertEqual(buck.get("LCSC", ""), "C2071056", "AP63205 LCSC part number must match BOM (C2071056)")

        # Verify inductor present for buck
        inductors = [s for s in symbols if s.get("Reference", "").startswith("L")]
        self.assertGreaterEqual(len(inductors), 1, "Buck inductor not found")

    def test_reverse_polarity_and_tvs(self):
        """POWER.kicad_sch must include AO3407A P-FET reverse polarity and SMAJ30CA TVS diode."""
        self.assertTrue(self.pwr_file.is_file())
        content = self.pwr_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        pfets = [s for s in symbols if "AO3407" in s.get("Value", "") or "AO3407" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(pfets), 1, "AO3407A P-FET reverse polarity protection not found")

        tvs = [s for s in symbols if "SMAJ30CA" in s.get("Value", "")]
        self.assertGreaterEqual(len(tvs), 1, "SMAJ30CA TVS clamp diode not found")

    def test_diode_oring_dual_1n5819(self):
        """POWER.kicad_sch must implement dual 1N5819 Schottky diode OR-ing between VBUS and 5V Buck."""
        self.assertTrue(self.pwr_file.is_file())
        content = self.pwr_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        diodes = [s for s in symbols if "1N5819" in s.get("Value", "") or "1N5819" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(diodes), 2, f"Expected 2x 1N5819 OR-ing diodes, found {len(diodes)}")

    def test_dual_3v3_ldos(self):
        """POWER.kicad_sch must capture AP7343-33 (3V3_SENS) and AP2112K-3.3 (3V3_MCU)."""
        self.assertTrue(self.pwr_file.is_file())
        content = self.pwr_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        
        sens_ldos = [s for s in symbols if "AP7343" in s.get("Value", "") or "AP7343" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(sens_ldos), 1, "AP7343-33 (3V3_SENS) LDO not found")
        self.assertEqual(sens_ldos[0].get("LCSC", ""), "C460383", "AP7343 LCSC part number must match BOM (C460383)")

        mcu_ldos = [s for s in symbols if "AP2112K" in s.get("Value", "") or "AP2112K" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(mcu_ldos), 1, "AP2112K-3.3 (3V3_MCU) LDO not found")
        self.assertEqual(mcu_ldos[0].get("LCSC", ""), "C51118", "AP2112K LCSC part number must match BOM (C51118)")

        labels = extract_labels(content)
        self.assertIn("3V3_SENS", labels, "3V3_SENS rail label missing from POWER sheet")
        self.assertIn("3V3_MCU", labels, "3V3_MCU rail label missing from POWER sheet")


class TestRootSchematicHierarchicalSheets(unittest.TestCase):
    def setUp(self):
        self.root_file = HW_DIR / "MADpilot-H7.kicad_sch"

    def test_root_contains_mcu_and_power_sheets(self):
        """Root schematic must instantiate MCU and POWER hierarchical sheets."""
        self.assertTrue(self.root_file.is_file(), f"Missing {self.root_file}")
        content = self.root_file.read_text(encoding="utf-8")
        
        # Check sheet references
        self.assertIn("MCU.kicad_sch", content, "MCU.kicad_sch not referenced in root sheet")
        self.assertIn("POWER.kicad_sch", content, "POWER.kicad_sch not referenced in root sheet")
        
        # Check sheet names
        self.assertIn('"Sheetname" "MCU"', content)
        self.assertIn('"Sheetname" "POWER"', content)

        # Check sheet instances in path
        sheet_inst_match = re.findall(r'\(path\s+"/[^"]*"\s+\(page\s+"([0-9]+)"\)\s*\)', content)
        self.assertGreaterEqual(len(sheet_inst_match), 3, "Root sheet must have at least 3 page instances (Root, MCU, POWER)")


if __name__ == "__main__":
    unittest.main()

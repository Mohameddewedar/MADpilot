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


def extract_sheets(content: str):
    """Extract child sheets from a root schematic."""
    sheet_matches = re.finditer(r'\(sheet\s+.*?\(property\s+"Sheetname"\s+"([^"]+)".*?\(property\s+"Sheetfile"\s+"([^"]+)"', content, re.DOTALL)
    return [(m.group(1), m.group(2)) for m in sheet_matches]


class TestStorageSchematic(unittest.TestCase):
    def setUp(self):
        self.storage_file = HW_DIR / "STORAGE.kicad_sch"

    def test_storage_schematic_exists_and_valid_sexp(self):
        """STORAGE.kicad_sch must exist and be valid KiCad 8 S-expression."""
        self.assertTrue(self.storage_file.is_file(), f"Missing {self.storage_file}")
        content = self.storage_file.read_text(encoding="utf-8")
        self.assertTrue(content.strip().startswith("(kicad_sch"), "Must begin with (kicad_sch")
        self.assertTrue(content.strip().endswith(")"), "Must end with ')'")
        open_count = content.count('(')
        close_count = content.count(')')
        self.assertEqual(open_count, close_count, f"Parenthesis mismatch: {open_count} open vs {close_count} close")

    def test_tf01a_microsd_socket_present(self):
        """Must contain TF-01A push-push MicroSD socket with LCSC C91145."""
        self.assertTrue(self.storage_file.is_file())
        content = self.storage_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        sd_syms = [
            s for s in symbols
            if "TF-01A" in s.get("Value", "") or "C91145" in s.get("LCSC", "") or "Micro_SD" in s.get("_lib_id", "") or "MicroSD" in s.get("Value", "")
        ]
        self.assertGreaterEqual(len(sd_syms), 1, "MicroSD socket symbol not found in STORAGE.kicad_sch")
        sd = sd_syms[0]
        self.assertEqual(sd.get("LCSC", ""), "C91145", "MicroSD socket LCSC part number must match C91145")

    def test_sdmmc1_signals_wired(self):
        """Must wire 4-bit SDMMC1 signals (D0-D3, CK, CMD)."""
        self.assertTrue(self.storage_file.is_file())
        content = self.storage_file.read_text(encoding="utf-8")
        labels = extract_labels(content)
        expected_sdmmc = {
            "SDMMC1_D0", "SDMMC1_D1", "SDMMC1_D2", "SDMMC1_D3",
            "SDMMC1_CK", "SDMMC1_CMD"
        }
        self.assertTrue(expected_sdmmc.issubset(labels), f"Missing SDMMC1 nets in STORAGE: {expected_sdmmc - labels}")

    def test_storage_pullups_and_decoupling(self):
        """Must contain 10k pull-up resistors on data/command lines and decoupling caps."""
        self.assertTrue(self.storage_file.is_file())
        content = self.storage_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)

        # 10k pull-ups (at least 5 for D0, D1, D2, D3, CMD)
        resistors = [s for s in symbols if s.get("Reference", "").startswith("R")]
        pullups_10k = [r for r in resistors if "10k" in r.get("Value", "").lower() or "10K" in r.get("Value", "")]
        self.assertGreaterEqual(len(pullups_10k), 5, f"Expected at least 5x 10k pull-up resistors, found {len(pullups_10k)}")

        # Decoupling capacitors
        caps = [s for s in symbols if s.get("Reference", "").startswith("C")]
        self.assertGreaterEqual(len(caps), 1, "Expected decoupling capacitor on MicroSD power rail")

        # Power rails
        labels = extract_labels(content)
        self.assertIn("3V3_MCU", labels, "3V3_MCU power rail label missing from STORAGE sheet")
        self.assertIn("GND", labels, "GND missing from STORAGE sheet")


class TestConnectorsSchematic(unittest.TestCase):
    def setUp(self):
        self.conn_file = HW_DIR / "CONNECTORS.kicad_sch"

    def test_connectors_schematic_exists_and_valid_sexp(self):
        """CONNECTORS.kicad_sch must exist and be valid KiCad 8 S-expression."""
        self.assertTrue(self.conn_file.is_file(), f"Missing {self.conn_file}")
        content = self.conn_file.read_text(encoding="utf-8")
        self.assertTrue(content.strip().startswith("(kicad_sch"), "Must begin with (kicad_sch")
        self.assertTrue(content.strip().endswith(")"), "Must end with ')'")
        open_count = content.count('(')
        close_count = content.count(')')
        self.assertEqual(open_count, close_count, f"Parenthesis mismatch: {open_count} open vs {close_count} close")

    def test_power_connectors_present_and_wired(self):
        """Captures POWER1 & POWER2 6-pin JST-GH connectors with voltage & current sense."""
        self.assertTrue(self.conn_file.is_file())
        content = self.conn_file.read_text(encoding="utf-8")
        labels = extract_labels(content)
        expected_power_nets = {"VOLTAGE1", "CURRENT1", "VOLTAGE2", "CURRENT2"}
        self.assertTrue(expected_power_nets.issubset(labels), f"Missing POWER sense nets: {expected_power_nets - labels}")

        # Check for 6-pin connector symbols
        symbols = extract_symbols(content)
        conn_6pin = [s for s in symbols if s.get("Reference", "").startswith("J") and ("01x06" in s.get("_lib_id", "") or "6" in s.get("Value", ""))]
        self.assertGreaterEqual(len(conn_6pin), 2, "Expected at least 2x 6-pin connectors for POWER1 & POWER2")

    def test_telem_connectors_present_and_wired(self):
        """Captures TELEM1 & TELEM2 6-pin JST-GH connectors with RTS/CTS hardware flow control."""
        self.assertTrue(self.conn_file.is_file())
        content = self.conn_file.read_text(encoding="utf-8")
        labels = extract_labels(content)
        expected_telem_nets = {
            "TELEM1_TX", "TELEM1_RX", "TELEM1_CTS", "TELEM1_RTS",
            "TELEM2_TX", "TELEM2_RX", "TELEM2_CTS", "TELEM2_RTS"
        }
        self.assertTrue(expected_telem_nets.issubset(labels), f"Missing TELEM nets: {expected_telem_nets - labels}")

    def test_gps_connectors_present_and_wired(self):
        """Captures GPS1 (10-pin JST-GH with safety switch, safety LED, buzzer) & GPS2 (6-pin JST-GH)."""
        self.assertTrue(self.conn_file.is_file())
        content = self.conn_file.read_text(encoding="utf-8")
        labels = extract_labels(content)
        expected_gps_nets = {
            "GPS1_TX", "GPS1_RX", "GPS2_TX", "GPS2_RX",
            "GPS_SCL", "GPS_SDA",
            "SAFETY_SW", "SAFETY_LED", "BUZZER"
        }
        self.assertTrue(expected_gps_nets.issubset(labels), f"Missing GPS nets: {expected_gps_nets - labels}")

        symbols = extract_symbols(content)
        conn_10pin = [s for s in symbols if s.get("Reference", "").startswith("J") and ("01x10" in s.get("_lib_id", "") or "10" in s.get("Value", ""))]
        self.assertGreaterEqual(len(conn_10pin), 1, "Expected at least 1x 10-pin connector for GPS1")

    def test_i2c_external_and_rc_connectors(self):
        """Captures I2C external port (4-pin JST-GH) and RC_IN (5-pin JST-GH with RSSI analog)."""
        self.assertTrue(self.conn_file.is_file())
        content = self.conn_file.read_text(encoding="utf-8")
        labels = extract_labels(content)
        expected_nets = {"EXT_I2C_SCL", "EXT_I2C_SDA", "RC_RX", "RSSI_ADC"}
        self.assertTrue(expected_nets.issubset(labels), f"Missing I2C or RC nets: {expected_nets - labels}")

    def test_usb_type_c_receptacle_and_protection(self):
        """Captures USB Type-C (TYPE-C-31-M-12, C165948) with 5.1k CC pull-downs, VBUS detect, and USBLC6-2P6 ESD clamp."""
        self.assertTrue(self.conn_file.is_file())
        content = self.conn_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)

        # USB Receptacle
        usb_syms = [s for s in symbols if "TYPE-C" in s.get("Value", "") or "C165948" in s.get("LCSC", "") or "USB_C" in s.get("_lib_id", "")]
        self.assertGreaterEqual(len(usb_syms), 1, "USB Type-C receptacle symbol not found")
        self.assertEqual(usb_syms[0].get("LCSC", ""), "C165948", "USB Type-C receptacle LCSC part must be C165948")

        # USBLC6 ESD Protection
        esd_syms = [s for s in symbols if "USBLC6" in s.get("Value", "") or s.get("LCSC", "") in ["C15999", "C7519"]]
        self.assertGreaterEqual(len(esd_syms), 1, "USBLC6-2P6 ESD clamp symbol not found")
        self.assertIn(esd_syms[0].get("LCSC", ""), ["C15999", "C7519"], "ESD clamp LCSC must match BOM (C15999 or C7519)")

        # 5.1k CC pull-down resistors
        resistors = [s for s in symbols if s.get("Reference", "").startswith("R")]
        cc_resistors = [r for r in resistors if "5.1k" in r.get("Value", "").lower()]
        self.assertGreaterEqual(len(cc_resistors), 2, f"Expected at least 2x 5.1k CC resistors, found {len(cc_resistors)}")

        # Net labels
        labels = extract_labels(content)
        expected_usb_nets = {"OTG_FS_DM", "OTG_FS_DP", "VBUS_DETECT"}
        self.assertTrue(expected_usb_nets.issubset(labels), f"Missing USB nets: {expected_usb_nets - labels}")

    def test_pwm_servo_rail_headers(self):
        """Captures 12-channel PWM servo rail headers grouped by TIM1 (1-4), TIM4 (5-8), TIM5 (9-12)."""
        self.assertTrue(self.conn_file.is_file())
        content = self.conn_file.read_text(encoding="utf-8")
        labels = extract_labels(content)
        for ch in range(1, 13):
            self.assertIn(f"PWM{ch}", labels, f"PWM{ch} missing from CONNECTORS sheet")


class TestDebugSchematic(unittest.TestCase):
    def setUp(self):
        self.debug_file = HW_DIR / "DEBUG.kicad_sch"

    def test_debug_schematic_exists_and_valid_sexp(self):
        """DEBUG.kicad_sch must exist and be valid KiCad 8 S-expression."""
        self.assertTrue(self.debug_file.is_file(), f"Missing {self.debug_file}")
        content = self.debug_file.read_text(encoding="utf-8")
        self.assertTrue(content.strip().startswith("(kicad_sch"), "Must begin with (kicad_sch")
        self.assertTrue(content.strip().endswith(")"), "Must end with ')'")
        open_count = content.count('(')
        close_count = content.count(')')
        self.assertEqual(open_count, close_count, f"Parenthesis mismatch: {open_count} open vs {close_count} close")

    def test_swd_header_present_and_wired(self):
        """DEBUG.kicad_sch captures a 4-pin SWD header (3V3_MCU, SWDIO, SWCLK, GND)."""
        self.assertTrue(self.debug_file.is_file())
        content = self.debug_file.read_text(encoding="utf-8")
        symbols = extract_symbols(content)
        header_syms = [s for s in symbols if s.get("Reference", "").startswith("J")]
        self.assertGreaterEqual(len(header_syms), 1, "Debug connector header not found")

        labels = extract_labels(content)
        expected_swd_nets = {"3V3_MCU", "SWDIO", "SWCLK", "GND"}
        self.assertTrue(expected_swd_nets.issubset(labels), f"Missing SWD nets: {expected_swd_nets - labels}")


class TestRootSchematicIntegrity(unittest.TestCase):
    def setUp(self):
        self.root_file = HW_DIR / "MADpilot-H7.kicad_sch"

    def test_root_instantiates_all_seven_sheets(self):
        """Root schematic instantiates all 7 child sheets."""
        self.assertTrue(self.root_file.is_file())
        content = self.root_file.read_text(encoding="utf-8")
        sheets = extract_sheets(content)
        sheet_files = {s[1] for s in sheets}
        expected_sheets = {
            "POWER.kicad_sch",
            "MCU.kicad_sch",
            "SENSORS.kicad_sch",
            "CAN.kicad_sch",
            "STORAGE.kicad_sch",
            "CONNECTORS.kicad_sch",
            "DEBUG.kicad_sch",
        }
        self.assertTrue(expected_sheets.issubset(sheet_files), f"Missing child sheets in root: {expected_sheets - sheet_files}")

    def test_sheet_instances_cover_pages_1_to_8(self):
        """Sheet instances path covers root and 7 sheets (pages 1 to 8)."""
        self.assertTrue(self.root_file.is_file())
        content = self.root_file.read_text(encoding="utf-8")
        pages = re.findall(r'\(page\s+"([0-9]+)"\)', content)
        page_set = set(pages)
        expected_pages = {str(i) for i in range(1, 9)}
        self.assertTrue(expected_pages.issubset(page_set), f"Missing pages: {expected_pages - page_set}")


if __name__ == "__main__":
    unittest.main()

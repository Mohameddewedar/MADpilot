# Upstream Identity Claims — MADpilot-H7

Status date: 2026-09-06  
Status: claimed-pending

This document records the upstream identity claims for the MADpilot-H7 Flight Controller, covering USB vendor/product identification and the ArduPilot bootloader board identifier.

---

## 1. USB Identity Claim

- **Vendor ID (VID)**: `0x1D50` (Openmoko Inc.)
- **Product ID (PID)**: `0x61a4` (sequential 4-byte aligned allocation following `0x61a0`)
- **Product Name**: MADpilot-H7
- **lsusb / Terse Description String**: `MADpilot-H7 flight controller`
- **Claim Status**: `claimed-pending` (pending merge of upstream pull request)
- **Pull Request URL**: https://github.com/openmoko/openmoko-usb-oui/pull/83

---

## 2. Process Correction: pid.codes vs openmoko-usb-oui

Issue tickets initially referenced the "pid.codes claims process" for USB PID allocation under VID 0x1D50. However, this conflates two separate community USB registries:

1. **pid.codes**: Administers **only** VID `0x1209` (a VID gifted to pid.codes, procured from USB-IF by a company that has since ceased trading — per the pid.codes FAQ). The pid.codes registry repository contains only a `1209` directory and processes allocations strictly for that VID.
   - Reference: [pid.codes Howto](https://pid.codes/howto/)
2. **openmoko-usb-oui**: Openmoko Inc.'s community registry administers VID `0x1D50` directly. Allocations under VID 0x1D50 are managed via pull requests modifying `usb_product_ids.psv` in the `openmoko/openmoko-usb-oui` GitHub repository.
   - Reference: [openmoko-usb-oui README](https://github.com/openmoko/openmoko-usb-oui)

Accordingly, MADpilot-H7's claim for PID `0x61a4` under VID `0x1D50` is submitted directly to `openmoko/openmoko-usb-oui`.

---

## 3. Firmware Encoding (ArduPilot hwdef.dat)

The claimed USB VID and PID are encoded into the ArduPilot board definition via directives in `hwdef.dat`:

```
USB_VENDOR 0x1D50
USB_PRODUCT 0x61a4
```

### Build-Time Processing

During firmware compilation:
1. ArduPilot's build tools execute `libraries/AP_HAL_ChibiOS/hwdef/scripts/chibios_hwdef.py`.
2. The `get_USB_IDs()` parser extracts `USB_VENDOR` and `USB_PRODUCT`.
3. The values are translated into preprocessor macros:
   - `HAL_USB_VENDOR_ID` (`0x1D50`)
   - `HAL_USB_PRODUCT_ID` (`0x61a4`)
4. These macros define the USB device descriptor presented to the host during enumeration.

The MADpilot-H7 board definition ticket will encode `0x1D50` and `0x61a4` directly into its `hwdef.dat`.

---

## 4. Bootloader Board ID Context

In addition to USB identity, ArduPilot flight controller boards require an `APJ_BOARD_ID` for bootloader board detection and `.apj` firmware packaging.

- **Board Identifier**: `APJ_BOARD_ID 3141`
- **Reserved Zone**: `3136–3145` (in the ArduPilot bootloader registry)
- **Status**: `claimed-pending`
- **Pull Request URL**: https://github.com/ArduPilot/ardupilot/pull/34310

Per ADR-0002, the MADpilot-H7 hardware adopts the Pixhawk-standard connector set for ecosystem compatibility while maintaining its own distinct board ID and USB identity.

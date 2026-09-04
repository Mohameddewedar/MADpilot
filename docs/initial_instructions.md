# Agent Instructions: Pixhawk FMU Hardware Replication (Phase 1)

## 1. Objective
Automate the retrieval, parsing, validation, and packaging of manufacturing files (Gerbers, BOM, CPL) required for a 1:1 hardware replication of the Pixhawk FMU open standard (Target: FMUv6X or FMUv6C). The final output must be formatted for Chinese turnkey PCBA services (e.g., JLCPCB/PCBWay).

## 2. Target Repositories
*   **Pixhawk Hardware Reference:** `https://github.com/pixhawk/hardware`
*   **Pixhawk Standards:** `https://github.com/pixhawk/Pixhawk-Standards`
*   *Note to Agent: If the user specifies a particular manufacturer's open-hardware fork (e.g., Holybro or CUAV reference designs), prioritize that specific URL.*

## 3. Execution Sequence

### Phase A: Repository Cloning & File Extraction
1.  Initialize a local workspace directory `/hardware_src`.
2.  Clone the target hardware repository into `/hardware_src`.
3.  Locate the specific hardware revision directory (e.g., `FMUv6X` core module).
4.  Extract the following mandatory files and copy them to a new output directory `/pcba_release`:
    *   **Gerber Files:** `.gbr`, `.gbo`, `.gtl`, `.gbl`, etc.
    *   **Drill Files:** `.drl` or `.xln`.
    *   **Bill of Materials (BOM):** `.csv` or `.xlsx`.
    *   **Component Placement List (CPL/POS):** `.csv`.
    *   **3D Models:** `.step` or `.stp` (required for enclosure design).

### Phase B: Data Validation & BOM Parsing
5.  Execute a Python script (using `pandas`) to parse the BOM and validate critical components:
    *   **MCU:** Must verify the presence of STM32H753 or STM32H743.
    *   **Sensors:** Must verify the presence of standard IMUs (e.g., ICM-42688-P, BMI088, BMM150).
    *   **Connectors (if modular):** Verify Hirose DF40 (100-pin and 50-pin) components.
6.  Flag missing LCSC part numbers. Generate a `bom_missing_lcsc.csv` report detailing any components requiring manual consignment.
7.  Verify package sizes against standard metric parameters (e.g., metric 1005 for 0402 imperial).

### Phase C: File Packaging & Formatting
8.  Compress all Gerber and Drill files into a single archive: `FMU_Gerbers.zip`.
9.  Reformat the BOM and CPL file headers to comply with JLCPCB/PCBWay automated ingest requirements:
    *   **BOM Columns:** `Comment`, `Designator`, `Footprint`, `LCSC Part Number`.
    *   **CPL Columns:** `Designator`, `Mid X`, `Mid Y`, `Layer`, `Rotation`.
10. Generate a `manufacturing_spec.txt` file detailing the bare board parameters:
    *   **Layers:** 8 (for FMUv6X core) or 6 (for FMUv6C/Baseboards).
    *   **Material:** FR-4 TG155.
    *   **Thickness:** 1.6 mm.
    *   **Copper Weight:** 35 µm (1 oz) inner and outer layers.
    *   **Surface Finish:** ENIG (Electroless Nickel Immersion Gold).
    *   **Impedance Control:** Yes.
    *   **Via Process:** Tenting or Epoxy filled (extract this from the reference design notes).

## 4. Error Handling Constraints
*   **Missing Files:** If any required extension (Gerber, BOM, CPL) is missing, halt execution immediately and output the missing file type to the terminal. Do not attempt to generate placeholder files.
*   **Architecture Mismatch:** If the MCU detected in the BOM is an STM32F4 or STM32F7 series, halt execution and flag an architecture version error (Phase 1 strictly requires H7 series).

## 5. Success Criteria
Execution is successful when `/pcba_release` contains exactly:
- `FMU_Gerbers.zip`
- `FMU_BOM_Formatted.csv`
- `FMU_CPL_Formatted.csv`
- `manufacturing_spec.txt`
- `board_3d_model.step`
- `bom_missing_lcsc.csv` (if applicable)
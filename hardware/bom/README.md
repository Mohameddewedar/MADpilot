# In-Stock-First BOM Snapshot Process

This directory documents and supports the **In-Stock-First** BOM snapshot process for the MADpilot-H7 Flight Controller.

Per [CONTEXT.md](../../CONTEXT.md), the **In-Stock-First** rule dictates:
> *A design may only freeze when every BOM part is procurable from the chosen assembly house at that moment.*

The goal of this process is absolute reproducibility: a later re-order must be able to reproduce the exact earlier build, with exact component part numbers, verified assembly house lifecycle states, and cryptographic integrity.

---

## When Snapshots Are Taken

Snapshots occur at every formal **Rev freeze** mapped directly to the milestone gates in [PLAN.md](../../PLAN.md):

1. **Rev A Freeze (Phase 1 — M2–M6)**:
   - **Trigger:** Gate **G0** (mandatory external schematic + layout review passed).
   - **Timing:** Immediately before placing the turnkey PCBA order (JLC 6-layer bare x10 + stencil + turnkey PCBA x5).
   - **Scope:** Freeze components including the STM32H743 LQFP-176, ICM-42605, BMI270, and MS5611.

2. **Rev B Freeze (Phase 2 — M6–M12)**:
   - **Trigger:** Gate **G8** (three consecutive clean autonomous test flights witnessed by pilots).
   - **Timing:** Prior to submitting the small-batch turnkey PCBA re-order (turnkey x5–10).
   - **Scope:** Complete Bill of Materials incorporating any fixes from Rev A bring-up.

---

## What Each Snapshot Contains

Each snapshot is stored in an immutable, dated directory under [snapshots/](snapshots/):
`hardware/bom/snapshots/<rev>-<YYYY-MM-DD>/`

Inside the directory:
1. **Original KiCad BOM CSV (`<bom_filename>.csv`)**:
   - The verbatim CSV export from KiCad at the moment design freeze was declared.
2. **Procurement State Record (`stock-state.csv`)**:
   - Pre-populated with the BOM's part numbers and descriptions, derived from [template/stock-state.template.csv](template/stock-state.template.csv).
   - Filled by the operator at freeze time with:
     - `stock_quantity`: Verified stock on hand at the assembly house (JLCPCB / LCSC).
     - `lifecycle_state`: Component lifecycle status (e.g. Active, NRND, EOL).
     - `unit_price`: Unit cost at order time.
     - `product_url`: Direct link to assembly house catalog item.
3. **Snapshot Manifest (`manifest.json`)**:
   - Formatted from [template/manifest.json](template/manifest.json), recording revision name, snapshot date, original BOM file name, operator notes, and part counts.
4. **Cryptographic Checksums (`SHA256SUMS`)**:
   - SHA-256 checksums covering every file in the snapshot directory (matching format of [template/SHA256SUMS](template/SHA256SUMS)).

---

## Who Runs It

The snapshot is executed by the **Hardware Lead / Program Core** (solo-professional core per [TEAM.md](../../docs/TEAM.md)) as part of the formal gate exit criteria before any purchase order is issued.

---

## Immutability Rule

Snapshots are **strictly immutable**. Once a snapshot directory is written:
- It must never be edited, updated, or overwritten.
- If component obsolescence or out-of-stock conditions force a BOM change before manufacturing, a new snapshot revision must be generated (e.g. `RevA1` or a new date stamp).
- The snapshot script will refuse to overwrite an existing snapshot directory.

---

## Execution Instructions

To generate a snapshot, run [scripts/snapshot_bom.py](../../scripts/snapshot_bom.py) from the repository root:

```bash
python scripts/snapshot_bom.py --bom path/to/kicad_bom.csv --rev RevA --notes "Rev A freeze for G0 order"
```

The script will:
1. Validate the input CSV.
2. Create `hardware/bom/snapshots/<rev>-<YYYY-MM-DD>/`.
3. Copy the BOM file.
4. Generate `stock-state.csv` pre-filled with part numbers.
5. Generate `manifest.json`.
6. Compute `SHA256SUMS` for the archive.

The operator then inspects JLCPCB/LCSC inventory, updates `stock-state.csv` with verified stock quantities and URLs, and commits the snapshot to version control.

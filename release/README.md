# MADpilot Release Staging Area

This directory is the staging ground for commercial and public releases of the MADpilot-H7 Flight Controller.

In accordance with [CONTEXT.md](../CONTEXT.md) and [ADR-0001](../docs/adr/0001-open-hardware-license-path.md), MADpilot maintains a continuous **Sell-Ready** posture:
> *Publication is one checklist away, never a project.*

During personal and educational development, no distribution occurs and design files remain private. However, the moment any Flight Controller board is sold or publicly distributed, legal obligations take effect immediately:
1. Modified KiCad hardware design files must be published under **CERN-OHL-S-2.0** ([release/licenses/CERN-OHL-S-2.0.txt](licenses/CERN-OHL-S-2.0.txt)).
2. Complete Corresponding Source code of the exact ArduPilot firmware shipped must be offered under **GNU GPLv3** ([release/licenses/GPL-3.0.txt](licenses/GPL-3.0.txt)).

This staging area contains pre-built templates, automation scripts, and verification checklists so that release activation can be executed on demand without scramble or delay.

---

## The Activation Checklist

This checklist maps 1:1 to the Sell-Ready **Prep-now** items defined in [PLAN.md](../PLAN.md):

### 1. Board ID 3141 Reservation Status
- **What "Done" Means**: Upstream Pull Request merged into ArduPilot's `Tools/AP_Bootloader/board_types.txt` reserving the 10-ID block 3136–3145 centered on pi (per convention), with ID `3141` assigned to `AP_HW_MADPILOT_H7` (and ODID variant `13141` if needed).
- **Where Artifact Lives**: Upstream ArduPilot bootloader registry (`Tools/AP_Bootloader/board_types.txt`), tracked via the pinned ArduPilot fork submodule ([ADR-0004](../docs/adr/0004-hub-repo-fork-submodule.md)), and configured in board hwdef files upon Phase 1 creation.
- **Current Status**: *Upstream PR filed and open*: [ArduPilot/ardupilot#34310](https://github.com/ArduPilot/ardupilot/pull/34310) (verified fallback gap IDs 1178, 1153, 1249 available if a collision is raised).

### 2. USB PID under VID 0x1D50 Claim Status
- **What "Done" Means**: Dedicated Product ID allocated under the Openmoko VID `0x1D50` via merged pull request to the `openmoko/openmoko-usb-oui` registry (the Openmoko VID administrator; pid.codes itself only administers VID 0x1209), with root [LICENSE](../LICENSE) established as prerequisite.
- **Where Artifact Lives**: Upstream `openmoko-usb-oui` registry records (`usb_product_ids.psv`) and referenced in board USB descriptors.
- **Current Status**: *Prerequisites met; PR submission queued* (Root [LICENSE](../LICENSE) file created; claim PR ready to be filed by orchestrator).

### 3. Trademark-Safe Naming Records
- **What "Done" Means**: The product is strictly and exclusively branded **MADpilot-H7**. In accordance with [ADR-0001](../docs/adr/0001-open-hardware-license-path.md), "Pixhawk" is never used in or adjacent to the product name, silkscreen, or marketing copy. Mentions of "Pixhawk" are strictly confined to factual compatibility statements (e.g. connector pinout compliance per [ADR-0002](../docs/adr/0002-pixhawk-standard-connectors.md)).
- **Where Artifact Lives**: Enforced in [LICENSE](../LICENSE), [CONTEXT.md](../CONTEXT.md), [ADR-0001](../docs/adr/0001-open-hardware-license-path.md), and [release/design-files/README.md](design-files/README.md).
- **Current Status**: *Active and strictly enforced* across all repository documentation and licensing artifacts.

### 4. Release Staging Area Infrastructure
- **What "Done" Means**: Publication packages and automation are established for CERN-OHL-S-2.0 hardware design publication and GPLv3 firmware source offer, including official license texts and package generator.
- **Where Artifact Lives**: This directory (`release/`), containing:
  - [licenses/CERN-OHL-S-2.0.txt](licenses/CERN-OHL-S-2.0.txt) & [licenses/GPL-3.0.txt](licenses/GPL-3.0.txt)
  - [design-files/README.md](design-files/README.md)
  - [source-offer/README.md](source-offer/README.md)
  - [source-offer/make_source_package.py](source-offer/make_source_package.py)
- **Current Status**: *Complete and operational*.

### 5. In-Stock-First BOM Snapshots at Every Rev Freeze
- **What "Done" Means**: Immutable, dated snapshots captured at each revision freeze (Rev A at Gate G0, Rev B at Gate G8) recording the exact KiCad BOM, verified per-part assembly house stock state (`stock-state.csv`), manifest, and cryptographic SHA256 checksums.
- **Where Artifact Lives**: [hardware/bom/README.md](../hardware/bom/README.md), [hardware/bom/snapshots/](../hardware/bom/snapshots/), and tooling in [scripts/snapshot_bom.py](../scripts/snapshot_bom.py).
- **Current Status**: *Tooling and workflow established*; snapshots trigger at Gate G0 order review.

---

## Defer-Until-Sale Items

These expensive items are deliberately deferred during Phase 0–2 until a formal decision to sell is made (per [PLAN.md](../PLAN.md)), but must be executed before shipping any units to paying customers:

1. **CE / FCC / RoHS Compliance Testing ($3,000–$10,000)**:
   - **What "Done" Means**: Formal EMC emission testing (FCC Part 15 Class B, CE EN 55032/EN 55035) and RoHS declaration of conformity issued by an accredited laboratory.
   - **Artifact Location**: Deferred until Phase 3 commercial sale decision (see cost allocation in [docs/COST-ESTIMATE.md](../docs/COST-ESTIMATE.md)); test reports and certificates to be archived upon completion.
   - **Trigger**: Batch >50 or public commercial sale decision.

2. **Egypt Sale-Legality Review**:
   - **What "Done" Means**: Written legal assessment of domestic Egyptian regulations concerning drone-adjacent avionics distribution, confirming domestic buyer exposure, ECAA aero-club arrangement alignment, and commercial entity requirements.
   - **Artifact Location**: Deferred until domestic commercial distribution (see Egypt operating rules in [PLAN.md](../PLAN.md)).
   - **Trigger**: Prior to offering units to domestic Egyptian buyers.

3. **Pricing and Per-Unit Economics Finalization**:
   - **What "Done" Means**: Finalized unit pricing factoring turnkey PCBA quotes, component yield buffers, packaging, import duties/VAT (14% VAT + 0–10% customs duty per [PLAN.md](../PLAN.md)), shipping, and support contingency.
   - **Artifact Location**: Documented in [docs/COST-ESTIMATE.md](../docs/COST-ESTIMATE.md).
   - **Trigger**: Prior to accepting customer pre-orders or sales.

---

## Directory Organization

- **[licenses/](licenses/)**: Contains the official, verbatim license texts:
  - [CERN-OHL-S-2.0.txt](licenses/CERN-OHL-S-2.0.txt)
  - [GPL-3.0.txt](licenses/GPL-3.0.txt)
- **[design-files/](design-files/README.md)**: Hardware publication package staging and CERN-OHL-S-2.0 attribution obligations.
- **[source-offer/](source-offer/README.md)**: ArduPilot GPLv3 source offer documentation, written offer template, and [make_source_package.py](source-offer/make_source_package.py).

# Rev A design evidence and order gates

These requirements make the approved Rev A design and the remaining implementation tickets checkable. They govern the Altium redraw and layout under ADRs 0001–0005. They record required future evidence; none of the gates below is asserted passed by publishing this document.

The [schematic requirements](rev-a-schematic-requirements.md) define capture content, [comparative review §7](comparative-review.md#7-the-madpilot-h7-pin-plan) defines the pin plan, and the [BOM process](../../hardware/bom/README.md) defines procurement evidence. LEVIA-H7 is the Base Design; Pixhawk 6C is the Reference Board. Retain upstream attribution in README, LICENSE, project metadata and schematic title blocks.

## Capture to routing

Before closing [Altium capture, outline, stackup and placement](https://github.com/Mohameddewedar/MADpilot/issues/16) and starting trace routing, commit:

- `hardware/MADpilot-H7/MADpilot-H7.PrjPcb`, root `MADpilot-H7.SchDoc`, the seven POWER/MCU/SENSORS/CAN/STORAGE/CONNECTORS/DEBUG `.SchDoc` files, and `MADpilot-H7.PcbDoc` with placed components.
- Libraries and models needed to open the project without missing dependencies.
- A completed schematic-requirements checklist mapping each item to sheet/net/reference and review evidence. Export a new eight-page Altium schematic PDF, clearly distinguished from the historical KiCad PDF.
- An Altium ERC report with zero errors and zero unresolved warnings, identified by project revision. Record the explanation and approval of any resolved warning disposition; do not silently suppress findings.
- A verbatim Altium BOM export reconciled against the historical Rev A BOM, with every part/quantity/footprint change and reference renumbering explained and approved by the Program Lead.
- Preliminary full-BOM qualification with dated assembly-house stock/lifecycle evidence for the intended quantity plus assembly spares. This enables layout; the final manufacturing freeze remains required before purchase.
- Board outline, mounting keep-outs, airframe fit, JLC06161H-3313 stackup and placement evidence, followed by recorded Program Lead approval of placement.

Historical KiCad ticket closure, the September 8 snapshot and the historical-BOM unit tests do not establish that this Altium gate has passed.

## Routing to review

The PCB engineer records the JLCPCB manufacturing-rule source and date, stackup dimensions/material parameters, and Altium rule/impedance profile used for this board. Archive the profile with the design; calculate trace geometry from that profile rather than copying widths from another board.

- USB D+/D− is one 90-ohm differential pair. SDMMC1 CK/CMD/D0–D3 are 50-ohm single-ended signals. Record tolerances, widths, pair spacing for USB, clock/data timing and skew budgets for SDMMC, and length constraints, with their engineering source and reviewer acceptance.
- Maintain continuous L2/L5 ground reference planes. Under both IMUs retain a solid, quiet L2 ground reference; exclude switching nodes and noisy/high-current routes beneath the sensors. A signal/power routing keep-out does not remove the ground plane. Respect package-specific mechanical and copper restrictions documented by the sensor manufacturers and reconcile them with the ground rule before approval.
- Deliver zero unrouted nets and an Altium DRC report with zero errors and zero unresolved warnings against the archived rule profile, linked to the routed design revision.

The [G0 Review Package delivery](https://github.com/Mohameddewedar/MADpilot/issues/18) contains the current Altium schematic PDF, verbatim BOM and its dated procurement evidence, pin plan, Reference Board delta, layout/plane/stackup renders, ERC/DRC reports and rule profile, and complete editable Altium archive. Identify the reviewed commit and archive checksums in a package manifest. The independent reviewer must be engaged before schematic capture completes; booking is an independent task, not blocked by routing.

## Review to order

Receiving a written report completes review delivery even if its verdict is fail. It does not authorize purchase. The [review corrections and order task](https://github.com/Mohameddewedar/MADpilot/issues/19) enforces all of the following before any Rev A order:

1. Every review finding has a disposition, evidence and owner. Resolve all critical/high findings and every condition of a conditional pass. Lower-severity items may be deferred only with written reviewer acceptance and Program Lead approval, a reason, and a follow-up ticket or named Rev.
2. A fail requires rework and another independent review. Obtain a pass for the final design revision, or written reviewer acceptance that every conditional-pass requirement is satisfied. Record the Program Lead's G0 approval against that revision. A changed schematic, component, footprint or layout invalidates the earlier approval until the reviewer accepts the resulting delta or re-reviews it.
3. Re-run ERC and DRC with zero errors and zero unresolved warnings. Preserve reports and warning dispositions for the final design revision.
4. Immediately before ordering, verify every BOM part's assembly-house availability and lifecycle for five assembled boards plus required assembly spares and seal a new dated manufacturing BOM snapshot, even if part numbers are unchanged. Follow the [BOM process](../../hardware/bom/README.md); stock-driven design changes return to step 2.
5. Generate Gerbers, Excellon drill files, BOM, CPL, assembly drawings and stackup specification from the exact approved design revision. Before upload, record the full design commit, G0 approval/report, final snapshot path and generated-output checksums in the manufacturing manifest. Add the order reference after submission. Freeze outputs before upload; any subsequent design change returns to step 2.

The order remains JLCPCB Standard PCBA: five assembled boards, ten bare six-layer PCBs and a stencil. Program Lead approval and current procurement/import checks precede purchase. This document does not place an order or record a technical G0 sign-off.

# Cost Estimate — Year 1 (12 months to flight-proven Rev B)

Solo-professional program (TEAM.md), Egypt-based, USD (EGP ~50/USD, volatile). Excludes gear already owned — see EQUIPMENT.md "verify owned" rows. All import lines include 14% VAT + 0–10% duty on CIF + ~3% card FX fee.

| Phase | Window | Contents | Low | High |
|---|---|---|---|---|
| Phase 0 — dev kit & firmware | M0–M2 | Dev board ($80–200, pending Q27), GNSS puck, SiK x2 bands, ESP32 bridge, bench gap-fill | $300 | $520 |
| Phase 1 — Rev A | M2–M6 | G0 external review, JLC bare boards + stencil, turnkey PCBA x5, shipping + import, hand-build consumables | $450 | $900 |
| Phase 2 — Rev B | M6–M12 | Turnkey PCBA x5–10, shipping + import, flight ops (local batteries, spares), crash budget, bench harness | $700 | $1,050 |
| Outsource-on-Stall contingency | — | Paid reviews/debug sessions when the free pool can't unblock | $200 | $400 |
| **Total** | | | **$1,650** | **$2,870** |

Midpoint ~$2,250 (~EGP 110k). CBE card caps can bite: some standard Egyptian cards cap international spend near EGP 25k/month (~$500) — split orders across months or use a bank wire if a single PCBA order exceeds the cap.

## Per-unit economics (informational; sale-triggered work excluded)

- Rev B BOM ~$55–75/board + PCBA fees + amortized PCB/tooling -> unit cost ~$85–120 at qty 5.
- At sale: design files must be published (ADR-0001), ArduPilot source offered (GPLv3), CE/FCC/RoHS testing budget $3k–10k, Egypt sale-legality review. All deferred to a sale decision; tracked in the Sell-Ready checklist.

## Confidence flags

- Duty % per HS line is unverified (assumed ~5% average for electronics assemblies) — check the tariff lookup at nafeza.gov.eg or ask a broker before the first order.
- 6-layer small-quantity JLC pricing is an estimate — run a live quote before freezing the Phase-1 budget.
- SiK radio prices assume Holybro V3 (~$59/pair) via AliExpress.
- EGP rate and CBE card rules change frequently — recheck at every purchase.

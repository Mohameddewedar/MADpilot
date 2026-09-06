# 0004 — Hub repo with the ArduPilot fork as a submodule

The MADpilot repo is the permanent project hub — `docs/`, `hardware/` (the KiCad project), `hwdef/` staging, `PLAN.md`. ArduPilot lives as a GitHub fork, pinned as a git submodule inside the hub; CI builds firmware artifacts from the pinned fork ref. The OEM layer (defaults.parm, `AP_CUSTOM_FIRMWARE_STRING`) lives in the fork; the board hwdef lives in the hub until it is upstreamed.

## Considered Options

- **Everything inside the fork** — rejected: work we control would live inside a repo we don't.
- **Two unrelated top-level repos** — rejected: no single source of truth for phases, gates, and docs.

## Consequences

- The fork rebases monthly onto the stable Plane branch; hub CI catches toolchain/rebase drift immediately.
- Upstreaming the board (optional, later) moves the hwdef from hub to master via PR; the hub keeps a vendored copy until that lands.

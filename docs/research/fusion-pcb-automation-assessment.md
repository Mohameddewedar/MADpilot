# Fusion PCB automation assessment

Research date: 2026-11-06. Scope: Autodesk capabilities and applicability to MADpilot-H7. This is research, not a change to the project's EDA decision. No live Fusion session, account entitlements, or manufactured board was tested.

## Findings supported by primary sources

### Educational Assistant usage is not documented as unlimited

Autodesk's October 2026 announcement specifies **10 monthly Flex tokens (beta) for Students/Educators**, refreshing monthly without carry-over. Educational users cannot currently purchase additional Assistant usage; agentic features become available again at refresh. Informational guidance remains available. These included tokens apply to eligible Assistant capabilities, not all Flex services. A special institutional entitlement would need account-specific evidence before budgeting around unlimited usage. [Autodesk announcement](https://www.autodesk.com/products/fusion-360/blog/changes-to-autodesk-assistant-in-autodesk-fusion-beginning-october-6th/)

### There are three different Autodesk Fusion MCP services

- **Desktop MCP:** drives a running local Fusion session. Autodesk's published bridge forwards to `http://127.0.0.1:<port>/mcp`, default port 27182. It requires Fusion running with MCP enabled in Preferences > General > API. [Autodesk implementation README](https://github.com/Autodesk/ai-integrations/blob/main/fusion/local-mcp-server/README.md)
- **Data MCP:** manages hubs, projects, folders, metadata and permissions. It should not be confused with PCB editing. [Autodesk Data MCP introduction](https://www.autodesk.com/products/fusion-360/blog/introducing-the-autodesk-fusion-data-mcp-server/)
- **Compute MCP:** public beta announced September 15, 2026. Autodesk explicitly describes electronics among the exposed toolsets, together with design and manufacturing. The announcement describes TypeScript execution, over 7,000 endpoints, two concurrent sessions per user, a one-hour session limit and termination after 15 minutes idle. Sessions must save/export before ending. Broad electronics coverage is not a verified guarantee of every PCB operation. [Autodesk Compute announcement](https://www.autodesk.com/products/fusion-360/blog/fusion-compute-mcp/)

Compute's current help lists design/CAM/assembly/document/export capabilities, dynamic tool discovery, active-license entitlement checks and OAuth sign-in. It does not enumerate a complete schematic-to-Gerber sequence. Verify the installed/discovered tool surface rather than inferring it from broad announcements. [Compute MCP documentation](https://help.autodesk.com/view/ADSKMCP/ENU/?guid=ADSKMCP_FusionComputeMcp_autodesk_fusion_compute_mcp_html)

### Electronics has automation paths, with uneven support

The public `adsk.electron` Python/C++ API is currently documented as a preview supporting reading, traversal, coordinate conversion and export. The same introduction explicitly excludes creating/editing layout content from this API release. This limitation must not be generalized to every internal command, MCP service or add-in. [Current Electronics API introduction](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ElectronicsIntro.htm)

Fusion Electronics also supports ULP programs and command scripts; scripts consist of Electronics commands. These provide another route for repeatable automation. [Autodesk ULP/script documentation](https://help.autodesk.com/cloudhelp/ENU/Fusion-ECAD/files/ECD-ULP-SCRIPT-ABOUT.htm)

One third-party implementation, `groundplane-studio/fusion-electronics-mcp`, documents schematic edits, placement, routing, checks, libraries and JLCPCB outputs. Its own README says whole-board autonomous routing is not complete and CAM Gerber export still requires a human in Fusion. It reports native MCP fallback limitations on current builds and recommends its add-in. These are the implementer's claims, not independent reliability measurements or Autodesk guarantees. This is evidence of possible scoped automation, not production qualification. [Implementation and limitations](https://github.com/groundplane-studio/fusion-electronics-mcp)

### Assistant's exact PCB authoring scope needs a capability test

The May 2026 release explicitly introduced contextual Electronics analysis: design/BOM summaries, connectivity and pin queries, hierarchy inspection, and DRC explanations. It explicitly stated that the May Assistant did not modify Electronics designs. [May release](https://www.autodesk.com/products/fusion-360/blog/may-2026-product-update-whats-new/)

The October release adds broader Assistant context, configuration rules, BOM property editing and assembly component replacement. Its Electronics section covers measurement, rules, drill documentation, pours and CAM publishing. It does **not** explicitly establish unrestricted schematic editing or autonomous PCB routing. Therefore the May limitation cannot safely be asserted as permanently universal, but the October update also does not establish turnkey PCB authoring. Test the specific build and toolset. [October release](https://www.autodesk.com/products/fusion-360/blog/october-2026-major-product-update-whats-new/)

### Educational licensing and Sell-Ready need deliberate handling

Autodesk defines educational purposes as learning or educational research and excludes commercial, professional and other for-profit use. Educational experimentation may fit that purpose; commercial development/manufacturing for sale requires an appropriate entitlement. A possible later sale does not by itself settle the current purpose. Do not assume that changing a license later automatically answers every historical-use question. [Autodesk definition](https://www.autodesk.com/company/educational-purposes), [Autodesk staff clarification for student entrepreneurship](https://forums.autodesk.com/t5/fusion-support-forum/entrepreneurial-student-amp-license-agreement/m-p/14252369)

## Project assessment and engineering recommendations

These are engineering judgments, not measured model performance claims.

The amended [ADR-0003](../adr/0003-base-design-sal-fc-primary.md), [CONTEXT.md](../../CONTEXT.md), and [hardware README](../../hardware/MADpilot-H7/README.md) establish a KiCad-native LEVIA-H7 Base Design with STM32H743IIT6 LQFP-176 adaptation, dual dissimilar IMUs, MS5611, independent sensor power and Pixhawk-standard connectors. Moving this design into Fusion is an EDA migration requiring connectivity, library mapping, constraints and manufacturing-output validation. A STEP export for mechanical work is a smaller, separable change.

The proposed orchestrator/implementer/reviewer pattern is promising for document extraction, explicit constraint creation, scripting, library audits, BOM checks and repeatable edits. Its limiting factors are accessible editing operations and objective feedback. Extra reasoning effort and debate do not establish electrical correctness. Use reviewers to find concrete evidence of defects in frozen artifacts, with datasheet pin/page references and reproducible checks.

Keep a single active writer per CAD document. Give the implementer a bounded edit and machine-readable acceptance criteria. Run read-back and schematic/board connectivity comparisons after edits, ERC/DRC against the intended stack-up and fabricator rules, then independent review. Review power sequencing, decoupling, oscillator/USB routing, return paths, IMU orientation/isolation and firmware pin mapping explicitly. Preserve the project's G0 external review and prototype bench verification.

Before considering migration, prove a small vertical slice in a copied test project: discover tools; inspect actual connectivity; create/connect a real part; place it; route a net and pour; run ERC/DRC; save/reopen; produce native editable sources plus BOM/CPL/Gerbers and validate pin-1/orientation/output layers. Record manual steps and recovery failures. Judge throughput and correction effort from this exercise, rather than an arbitrary automation percentage.

For the current MADpilot-H7 phase, retain KiCad as the source of truth and use Fusion for enclosure/connector fit unless this proof demonstrates enough benefit to justify migration. Even if unlimited Assistant tokens were available under a special entitlement, the integration and verification limits would remain.

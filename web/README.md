# MADpilot Follow-up App v1

A local-only, read-only Flask web app that provides a workspace dashboard for the MADpilot flight controller project.

The Follow-up App renders real project files directly from the repository at request time—no project content or inventory is ever hardcoded.

## Features

- **Docs Browser (Lane 1)**:
  - Curated documentation inventory scanned via runtime globs: `docs/**`, `PLAN.md`, `CONTEXT.md`, `docs/adr/**`, and `hardware/bom/**`.
  - Complete isolation: the `ardupilot/` submodule directory is strictly excluded and never served or globbed.
  - Markdown rendering powered by `python-markdown` with `wikilinks`, `toc`, `tables`, `fenced_code`, and `codehilite` (Pygments).
  - Source-aware link rewriting: relative links and image paths are resolved against the source file's real disk location.
  - Broken link detection: invalid or non-existent file targets are flagged visibly with styling and badges rather than failing silently.
  - Dedicated Architecture Decision Record (ADR) index at `/docs/adr/`.
  - Raw workspace asset server at `/md/<path>` with strict path containment checks.
- **Tolerant Modular Architecture**:
  - `web.server.create_app()` dynamically scans candidate feature modules (`docs`, `progress`, `github_issues`) in a tolerant loop.
  - Features land independently across lanes; missing features render as clearly-marked "not yet built" without breaking the dashboard or docs browser.
- **Vendored HTMX**:
  - HTMX 2.x is vendored locally in `web/static/js/htmx.min.js`. No CDN or external network requests are made at runtime.
- **Plain, Dense Styling**:
  - Fast, responsive personal-tool styling in `web/static/css/app.css` with zero external CSS frameworks.

## Quick Start

### 1. Install dependencies

Ensure you are using Python 3.14+ (or compatible virtual environment):

```bash
python -m pip install -r web/requirements.txt
```

Verified pinned dependencies:
- `flask==3.1.3`
- `markdown==3.10.3`
- `pygments==2.21.0`
- `watchdog==6.0.0`

### 2. Run the application

From the repository root:

```bash
python -m web
```

The application will start on `http://127.0.0.1:8765`.

To specify custom host or port:

```bash
PORT=9000 HOST=127.0.0.1 python -m web
```

## Route Map

| Route | Description |
|---|---|
| `/` | Dashboard: project metrics and feature links (Docs, Progress, Issues) |
| `/docs/` | Live curated documentation inventory with instant search filter |
| `/docs/<path>` | Rendered Markdown document (validated against curated subset) |
| `/docs/adr/` | ADR index page listing `docs/adr/*.md` with titles and metadata |
| `/md/<path>` | Serves raw workspace assets (images, schematics, CSVs) referenced by docs |
| `/progress` | Progress tracker view (owned by Lane 2) |
| `/issues` | GitHub issues view (owned by Lane 3) |

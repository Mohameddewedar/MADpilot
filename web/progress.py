"""
MADpilot Follow-up App — Progress Tracker (Lane 2)

This module parses PLAN.md into a structured, machine-readable JSON schema,
persists the last-known-good parse to a disk cache (web/.cache/progress-cache.json),
and provides a Flask Blueprint for rendering the progress dashboard.

Gate Status Semantics:
- The plan does not yet mark gates as met; derive "met" only from explicit markers if present.
- Status values are strictly one of: "met", "not-met", or "not-reached".
- "met": derived ONLY from explicit markers in the gate line/title (e.g. "✅", "[x]", "(met)", "(passed)").
- "not-met": derived ONLY when a gate is explicitly marked failed (e.g. "❌", "(failed)", "(not-met)", "(not met)").
- "not-reached": assigned to any gate that lacks an explicit met or failed marker (including all gates after the
  highest explicitly-met gate, or all gates if none are explicitly marked met).
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from typing import Any

from flask import Blueprint, render_template

bp = Blueprint("progress", __name__, url_prefix="/progress")


class PlanParseError(Exception):
    """Raised when PLAN.md has missing or unparseable required sections or tables."""
    pass


def _clean_cell(text: str) -> str:
    """Clean a markdown table cell, stripping leading/trailing whitespace and outer formatting."""
    t = text.strip()
    # Strip wrapping bold markers if the entire cell is wrapped
    m = re.match(r'^\*{1,2}(.*?)\*{1,2}$', t)
    if m:
        t = m.group(1).strip()
    return t


def _parse_table_rows(section_text: str) -> tuple[list[str], list[list[str]]]:
    """
    Extract headers and data rows from a markdown table in section_text.
    Robust to minor formatting drift (bold markers in headers/cells, variable spacing).
    """
    lines = [line.strip() for line in section_text.splitlines() if line.strip()]
    table_lines: list[str] = []
    for line in lines:
        if line.startswith('|') and line.endswith('|'):
            table_lines.append(line)
        elif table_lines:
            # Table ended
            break

    if len(table_lines) < 3:
        raise PlanParseError("Markdown table not found or has insufficient rows (header + separator + data required)")

    # Parse raw headers
    raw_headers = [c.strip() for c in table_lines[0].split('|')[1:-1]]
    # Clean header names (strip bold, lower)
    headers = [re.sub(r'[*_#]', '', h).strip().lower() for h in raw_headers]

    # Verify separator line
    sep = table_lines[1]
    if not re.match(r'^\|(?:\s*:?-+:?\s*\|)+$', sep):
        raise PlanParseError(f"Malformed markdown table separator: {sep}")

    rows: list[list[str]] = []
    for line in table_lines[2:]:
        cells = [_clean_cell(c) for c in line.split('|')[1:-1]]
        # In case row has fewer cells than headers, pad with empty strings
        if len(cells) < len(headers):
            cells.extend([''] * (len(headers) - len(cells)))
        rows.append(cells[:len(headers)])

    return headers, rows


def _extract_sections(plan_md_text: str) -> dict[str, str]:
    """Split markdown text into sections keyed by normalized heading."""
    sections: dict[str, list[str]] = {}
    current_key: str | None = None

    for line in plan_md_text.splitlines():
        heading_match = re.match(r'^(#{1,6})\s+(.*?)\s*$', line)
        if heading_match:
            current_key = heading_match.group(2).strip().lower()
            sections[current_key] = []
        elif current_key is not None:
            sections[current_key].append(line)

    return {k: "\n".join(v) for k, v in sections.items()}


def _find_section(sections: dict[str, str], keyword: str) -> str:
    """Find section content matching keyword substring in heading."""
    kw = keyword.lower()
    for heading, text in sections.items():
        if kw in heading:
            return text
    raise PlanParseError(f"Required section matching '{keyword}' not found in PLAN.md")


def _evaluate_gate_status(raw_text: str) -> str:
    """
    Evaluate status for a gate segment.
    Only explicit markers mark a gate 'met' or 'not-met'; otherwise 'not-reached'.
    """
    if re.search(r'❌|\[failed\]|\((?:failed|not-met|not met|fail)\)', raw_text, re.IGNORECASE):
        return "not-met"
    if re.search(r'✅|\[x\]|\((?:met|passed|done)\)|\[(?:met|passed|done)\]', raw_text, re.IGNORECASE):
        return "met"
    return "not-reached"


def parse_plan(plan_md_text: str) -> dict[str, Any]:
    """
    Parse PLAN.md text into schema_version 1 structure.

    Returns:
        {
            "schema_version": 1,
            "generated_at": <iso-utc>,
            "phases": [{"name", "window", "goal", "exit_gate"}...],
            "gates": [{"id", "title", "status"}...],
            "action_items": [...],
            "improvement_backlog": [{"number", "entry", "gate"}...]
        }
    Raises:
        PlanParseError: if required sections or tables are missing or unparseable.
    """
    if not plan_md_text or not plan_md_text.strip():
        raise PlanParseError("PLAN.md content is empty")

    sections = _extract_sections(plan_md_text)

    # 1. Phases: "Program overview" table
    overview_text = _find_section(sections, "program overview")
    headers, rows = _parse_table_rows(overview_text)

    # Map headers to schema keys
    phase_idx = next((i for i, h in enumerate(headers) if "phase" in h), 0)
    window_idx = next((i for i, h in enumerate(headers) if "window" in h), 1)
    goal_idx = next((i for i, h in enumerate(headers) if "goal" in h), 2)
    gate_idx = next((i for i, h in enumerate(headers) if "exit" in h or "gate" in h), 3)

    phases = []
    for r in rows:
        phases.append({
            "name": r[phase_idx] if phase_idx < len(r) else "",
            "window": r[window_idx] if window_idx < len(r) else "",
            "goal": r[goal_idx] if goal_idx < len(r) else "",
            "exit_gate": r[gate_idx] if gate_idx < len(r) else "",
        })

    if not phases:
        raise PlanParseError("No phase rows parsed from 'Program overview' table")

    # 2. Phase gates: G0–G9
    gates_text = _find_section(sections, "phase gates")
    gates = []

    for line in gates_text.splitlines():
        sline = line.strip()
        if not sline:
            continue
        # Strip leading bullet if present
        sline = re.sub(r'^[-*]\s*', '', sline)
        # Handle multiple gates per bullet separated by middle dot or bullet (e.g. G3 · G4 · G5 · G6)
        segments = re.split(r'\s*[·•]\s*', sline)
        for seg in segments:
            seg = seg.strip()
            # Match gate id like **G0**, **G1**, G0, etc.
            m = re.match(r'^\*{0,2}(G\d+)\*{0,2}\s*(?:[:\-–—]\s*)?(.*)$', seg, re.IGNORECASE)
            if m:
                gid = m.group(1).upper()
                raw_title = m.group(2).strip()
                status = _evaluate_gate_status(seg)
                # Clean any explicit status marker from the title itself
                cleaned_title = re.sub(r'^\s*(?:✅|❌|\[[ xX]\]|\((?:met|passed|done|failed|not-met|not met)\)|\[(?:met|passed|done|failed)\])\s*[:\-–—]?\s*', '', raw_title)
                cleaned_title = re.sub(r'\s*[:\-–—]?\s*(?:✅|❌|\[[ xX]\]|\((?:met|passed|done|failed|not-met|not met)\)|\[(?:met|passed|done|failed)\])\s*$', '', cleaned_title)
                gates.append({
                    "id": gid,
                    "title": cleaned_title.strip(),
                    "status": status,
                })

    if not gates:
        raise PlanParseError("No gates found in 'Phase gates' section")

    # 3. Action items: "Action items" list
    action_text = _find_section(sections, "action items")
    action_items = []
    current_action: list[str] = []

    for line in action_text.splitlines():
        sline = line.strip()
        if not sline:
            continue
        # Check if new item (numbered e.g. '1.' or bullet '-' or '*')
        m = re.match(r'^(?:\d+[\.\)]|[-*]|\+)\s+(.*)$', sline)
        if m:
            if current_action:
                action_items.append(" ".join(current_action).strip())
            current_action = [m.group(1).strip()]
        elif current_action:
            # Continuation line
            current_action.append(sline)

    if current_action:
        action_items.append(" ".join(current_action).strip())

    if not action_items:
        raise PlanParseError("No action items found in 'Action items' section")

    # 4. Improvement Backlog: table
    backlog_text = _find_section(sections, "improvement backlog")
    b_headers, b_rows = _parse_table_rows(backlog_text)

    num_idx = next((i for i, h in enumerate(b_headers) if h in ("#", "num", "number", "id")), 0)
    entry_idx = next((i for i, h in enumerate(b_headers) if "entry" in h or "item" in h or "description" in h), 1)
    gate_col_idx = next((i for i, h in enumerate(b_headers) if "gate" in h or "phase" in h or "when" in h), 2)

    improvement_backlog = []
    for r in b_rows:
        raw_num = r[num_idx] if num_idx < len(r) else ""
        num_clean = re.sub(r'[*_]', '', raw_num).strip()
        parsed_num = int(num_clean) if num_clean.isdigit() else num_clean

        entry_val = r[entry_idx] if entry_idx < len(r) else ""
        gate_val = r[gate_col_idx] if gate_col_idx < len(r) else ""

        improvement_backlog.append({
            "number": parsed_num,
            "entry": entry_val,
            "gate": gate_val,
        })

    if not improvement_backlog:
        raise PlanParseError("No rows found in 'Improvement Backlog' table")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phases": phases,
        "gates": gates,
        "action_items": action_items,
        "improvement_backlog": improvement_backlog,
    }


def load_progress(
    plan_path: Path | str | None = None,
    cache_path: Path | str | None = None,
) -> dict[str, Any]:
    """
    Read PLAN.md from disk, parse it, and cache the last-good JSON to disk.

    Cache file location: web/.cache/progress-cache.json (includes 'cached_at' ISO timestamp).

    On PlanParseError or file error:
        Returns cached JSON if available, augmented with metadata:
        {"error": str, "cached_at": ...}.
        If no cache exists, returns an error payload indicating failure.
    """
    web_dir = Path(__file__).resolve().parent
    if plan_path is None:
        # Repo root is parent of web/
        repo_root = web_dir.parent
        resolved_plan_path = repo_root / "PLAN.md"
    else:
        resolved_plan_path = Path(plan_path)

    if cache_path is None:
        cache_dir = web_dir / ".cache"
        resolved_cache_path = cache_dir / "progress-cache.json"
    else:
        resolved_cache_path = Path(cache_path)
        cache_dir = resolved_cache_path.parent

    try:
        with open(resolved_plan_path, "r", encoding="utf-8") as f:
            plan_text = f.read()

        parsed = parse_plan(plan_text)
        now_iso = datetime.now(timezone.utc).isoformat()
        parsed["cached_at"] = now_iso

        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            with open(resolved_cache_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)
        except OSError:
            # Tolerant if filesystem write encounters permission or read-only error
            pass

        return parsed

    except (PlanParseError, OSError, Exception) as exc:
        err_msg = str(exc)
        if resolved_cache_path.is_file():
            try:
                with open(resolved_cache_path, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                cached["error"] = err_msg
                if "cached_at" not in cached:
                    mtime = resolved_cache_path.stat().st_mtime
                    cached["cached_at"] = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
                return cached
            except Exception:
                pass

        # No cache exists
        return {
            "error": err_msg,
            "cached_at": None,
            "schema_version": 1,
            "phases": [],
            "gates": [],
            "action_items": [],
            "improvement_backlog": [],
        }


def _compute_current_phase(phases: list[dict[str, Any]], gates: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Derive the active phase from parsed phases and gate progression."""
    if not phases:
        return None
    # If G0 not met or no gates yet, Phase 0 is current
    return phases[0]


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
def progress_view():
    """Render the progress dashboard with current or cached progress data."""
    data = load_progress()
    phases = data.get("phases", [])
    gates = data.get("gates", [])
    current_phase = _compute_current_phase(phases, gates)

    return render_template(
        "progress.html",
        progress=data,
        schema_version=data.get("schema_version", 1),
        generated_at=data.get("generated_at"),
        cached_at=data.get("cached_at"),
        error=data.get("error"),
        phases=phases,
        gates=gates,
        action_items=data.get("action_items", []),
        improvement_backlog=data.get("improvement_backlog", []),
        current_phase=current_phase,
    )

"""GitHub issues view for Follow-up App v1 (Lane 3).

Provides a Flask Blueprint ('bp', url_prefix="/issues") and standalone functions
to fetch, group, render, and cache GitHub issues for Mohameddewedar/MADpilot.
"""

from datetime import datetime, timezone
import html
import json
import os
from pathlib import Path
import subprocess

from flask import Blueprint, Response, render_template, request

DEFAULT_REPO = os.environ.get("GH_REPO", "Mohameddewedar/MADpilot")

bp = Blueprint("issues", __name__, url_prefix="/issues")


class GhUnavailable(Exception):
    """Raised when gh CLI invocation fails, is offline, or unauthenticated."""

    def __init__(self, message: str, exit_code: int = 1, stderr: str = ""):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.stderr = stderr or message


def _get_cache_path() -> Path:
    """Return the absolute path to the issues cache file."""
    return Path(__file__).resolve().parent / ".cache" / "issues-cache.json"


def label_contrast_color(hex_color: str) -> str:
    """Determine black or white foreground text for a given 6-char hex background color."""
    clean_hex = hex_color.lstrip("#")
    if len(clean_hex) == 6:
        try:
            r = int(clean_hex[0:2], 16)
            g = int(clean_hex[2:4], 16)
            b = int(clean_hex[4:6], 16)
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            return "#111111" if luminance > 160 else "#ffffff"
        except ValueError:
            pass
    return "#ffffff"


@bp.app_template_filter("contrast_color")
def _contrast_color_filter(hex_color: str) -> str:
    return label_contrast_color(hex_color)


def fetch_issues(repo: str | None = None) -> list[dict]:
    """Fetch open issues from GitHub via gh CLI.

    Runs `gh issue list -R <repo> --state open --limit 100 --json number,title,state,labels,assignees,updatedAt,url`
    Parses JSON output directly. Raises GhUnavailable on non-zero exit code.
    """
    target_repo = repo or os.environ.get("GH_REPO", DEFAULT_REPO)
    cmd = [
        "gh",
        "issue",
        "list",
        "-R",
        target_repo,
        "--state",
        "open",
        "--limit",
        "100",
        "--json",
        "number,title,state,labels,assignees,updatedAt,url",
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
    except FileNotFoundError as exc:
        raise GhUnavailable(f"gh CLI binary not found on PATH: {exc}", exit_code=1, stderr=str(exc))
    except subprocess.TimeoutExpired as exc:
        raise GhUnavailable("gh issue list timed out after 30 seconds", exit_code=1, stderr=str(exc))
    except Exception as exc:
        raise GhUnavailable(f"Failed to execute gh issue list: {exc}", exit_code=1, stderr=str(exc))

    if proc.returncode != 0:
        tail = proc.stderr.strip()
        raise GhUnavailable(
            f"gh issue list failed with exit code {proc.returncode}: {tail}",
            exit_code=proc.returncode,
            stderr=tail,
        )

    try:
        data = json.loads(proc.stdout)
        if not isinstance(data, list):
            raise ValueError(f"Expected list of issues, got {type(data)}")
        return data
    except Exception as exc:
        raise GhUnavailable(
            f"Failed to parse gh issue list output as JSON: {exc}",
            exit_code=1,
            stderr=proc.stderr.strip(),
        )


def group_issues(issues: list[dict]) -> dict[str, list[dict]]:
    """Group issues by labels of interest:
      - wayfinder: labels starting with 'wayfinder:'
      - ready: labels 'ready-for-agent' or 'ready-for-human'
      - work: labels 'bug' or 'enhancement'
      - other: issues matching none of the above

    Deduplicates by issue number within each group.
    """
    groups: dict[str, list[dict]] = {
        "wayfinder": [],
        "ready": [],
        "work": [],
        "other": [],
    }
    seen: dict[str, set[int]] = {
        "wayfinder": set(),
        "ready": set(),
        "work": set(),
        "other": set(),
    }

    for issue in issues:
        num = issue.get("number")
        raw_labels = issue.get("labels", []) or []
        label_names = [
            lbl.get("name", "") if isinstance(lbl, dict) else str(lbl)
            for lbl in raw_labels
        ]

        in_wayfinder = any(name.startswith("wayfinder:") for name in label_names)
        in_ready = any(name in ("ready-for-agent", "ready-for-human") for name in label_names)
        in_work = any(name in ("bug", "enhancement") for name in label_names)

        matched = False
        if in_wayfinder:
            if num not in seen["wayfinder"]:
                seen["wayfinder"].add(num)
                groups["wayfinder"].append(issue)
            matched = True
        if in_ready:
            if num not in seen["ready"]:
                seen["ready"].add(num)
                groups["ready"].append(issue)
            matched = True
        if in_work:
            if num not in seen["work"]:
                seen["work"].add(num)
                groups["work"].append(issue)
            matched = True

        if not matched:
            if num not in seen["other"]:
                seen["other"].add(num)
                groups["other"].append(issue)

    return groups


_BODY_CACHE: dict[int, str] = {}


def body_html(issue_number: int, repo: str | None = None) -> str:
    """Fetch raw issue body via `gh issue view <n> --json body` and render
    via `gh api markdown -f text=<raw body> -f mode=gfm`.
    Degrades to raw markdown in <pre> if the markdown API fails.
    """
    if issue_number in _BODY_CACHE:
        return _BODY_CACHE[issue_number]

    target_repo = repo or os.environ.get("GH_REPO", DEFAULT_REPO)
    cmd_view = [
        "gh",
        "issue",
        "view",
        str(issue_number),
        "-R",
        target_repo,
        "--json",
        "body",
    ]
    try:
        proc_view = subprocess.run(
            cmd_view,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        if proc_view.returncode != 0:
            tail = proc_view.stderr.strip()
            return f"<pre class=\"error\">Error fetching issue #{issue_number}: {html.escape(tail)}</pre>"
        data = json.loads(proc_view.stdout)
        raw_body = data.get("body", "") or ""
    except Exception as exc:
        return f"<pre class=\"error\">Error viewing issue #{issue_number}: {html.escape(str(exc))}</pre>"

    if not raw_body.strip():
        result = "<p class=\"no-body\"><em>No description provided.</em></p>"
        _BODY_CACHE[issue_number] = result
        return result

    cmd_md = [
        "gh",
        "api",
        "markdown",
        "-f",
        f"text={raw_body}",
        "-f",
        "mode=gfm",
    ]
    try:
        proc_md = subprocess.run(
            cmd_md,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        if proc_md.returncode == 0 and proc_md.stdout:
            result = proc_md.stdout
        else:
            result = f"<pre class=\"raw-markdown\">{html.escape(raw_body)}</pre>"
    except Exception:
        result = f"<pre class=\"raw-markdown\">{html.escape(raw_body)}</pre>"

    _BODY_CACHE[issue_number] = result
    return result


def load_issues(repo: str | None = None) -> dict:
    """Orchestrate issue loading with cached-dated fallback.

    Tries fetch_issues:
      - On success: writes web/.cache/issues-cache.json with fresh "cached_at" timestamp
        and returns {"issues": ..., "cached_at": ..., "degraded": False}.
      - On GhUnavailable: reads cached web/.cache/issues-cache.json and returns
        {"issues": ..., "cached_at": ..., "degraded": True, "error_kind": "offline"|"unauth", "gh_stderr": tail}.
      - If no cache exists + failure: includes "no_cache": True.
    """
    target_repo = repo or os.environ.get("GH_REPO", DEFAULT_REPO)
    cache_file = _get_cache_path()

    try:
        issues = fetch_issues(repo=target_repo)
        now_iso = datetime.now(timezone.utc).isoformat()
        cache_data = {
            "issues": issues,
            "cached_at": now_iso,
        }
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps(cache_data, indent=2), encoding="utf-8")
        except Exception:
            pass  # Non-fatal if cache write fails
        return {
            "issues": issues,
            "cached_at": now_iso,
            "degraded": False,
        }
    except GhUnavailable as err:
        if cache_file.is_file():
            try:
                cached_data = json.loads(cache_file.read_text(encoding="utf-8"))
                cached_issues = cached_data.get("issues", [])
                cached_at = cached_data.get("cached_at")
                if cached_at and isinstance(cached_issues, list):
                    error_kind = "unauth" if err.exit_code == 4 else "offline"
                    return {
                        "issues": cached_issues,
                        "cached_at": cached_at,
                        "degraded": True,
                        "error_kind": error_kind,
                        "gh_stderr": err.stderr,
                    }
            except Exception:
                pass

        error_kind = "unauth" if err.exit_code == 4 else "offline"
        return {
            "issues": [],
            "cached_at": None,
            "degraded": True,
            "no_cache": True,
            "error_kind": error_kind,
            "gh_stderr": err.stderr,
        }


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
def issues_view():
    """Render GitHub issues view with grouping and degraded-state handling."""
    expand_param = request.args.get("expand", "")
    expanded_issue = None
    expand_all = False
    if expand_param == "all":
        expand_all = True
    elif expand_param.isdigit():
        expanded_issue = int(expand_param)

    data = load_issues()

    if data.get("no_cache"):
        return render_template(
            "issues.html",
            no_cache=True,
            degraded=True,
            error_kind=data.get("error_kind", "offline"),
            gh_stderr=data.get("gh_stderr", ""),
            cached_at=None,
            groups={"wayfinder": [], "ready": [], "work": [], "other": []},
            sections=[],
            contrast_color=label_contrast_color,
            body_html=body_html,
        )

    issues = data.get("issues", [])
    groups = group_issues(issues)

    ready_agent = [
        iss for iss in groups["ready"]
        if any(
            (lbl.get("name") if isinstance(lbl, dict) else str(lbl)) == "ready-for-agent"
            for lbl in iss.get("labels", [])
        )
    ]
    ready_human = [
        iss for iss in groups["ready"]
        if any(
            (lbl.get("name") if isinstance(lbl, dict) else str(lbl)) == "ready-for-human"
            for lbl in iss.get("labels", [])
        )
    ]

    sections = [
        {
            "id": "wayfinder",
            "title": "Wayfinder tickets",
            "description": "Wayfinder milestone and track tickets (wayfinder:*)",
            "issues": groups["wayfinder"],
        },
        {
            "id": "ready-agent",
            "title": "Ready-for-agent",
            "description": "Approved specs ready for autonomous implementation",
            "issues": ready_agent,
        },
        {
            "id": "ready-human",
            "title": "Ready-for-human",
            "description": "Tasks requiring human implementation or physical hardware action",
            "issues": ready_human,
        },
        {
            "id": "work",
            "title": "Bugs & enhancements",
            "description": "Active development items (bug, enhancement)",
            "issues": groups["work"],
        },
        {
            "id": "other",
            "title": "Other",
            "description": "Other open issues",
            "issues": groups["other"],
        },
    ]

    return render_template(
        "issues.html",
        no_cache=False,
        degraded=data.get("degraded", False),
        cached_at=data.get("cached_at"),
        error_kind=data.get("error_kind"),
        gh_stderr=data.get("gh_stderr", ""),
        groups=groups,
        sections=sections,
        expanded_issue=expanded_issue,
        expand_all=expand_all,
        contrast_color=label_contrast_color,
        body_html=body_html,
    )


@bp.route("/body/<int:issue_number>", methods=["GET"])
def issue_body_view(issue_number: int):
    """Return rendered GFM HTML body for a single issue (for HTMX dynamic loading)."""
    rendered = body_html(issue_number)
    return Response(rendered, mimetype="text/html")

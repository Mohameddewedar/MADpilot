"""Documentation browser blueprint for Follow-up App v1.

Curated docs inventory via runtime glob, safe path validation, and markdown
rendering with link rewriting against source file disk locations.
"""

from __future__ import annotations

import datetime
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

from flask import Blueprint, abort, render_template, request, send_file
import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

REPO_ROOT = Path(__file__).resolve().parent.parent

CURATED_GLOBS = [
    "PLAN.md",
    "CONTEXT.md",
    "docs/**/*.md",
    "docs/adr/**/*.md",
    "hardware/bom/**/*.md",
]

bp = Blueprint("docs", __name__)


def is_ardupilot_path(path: Path) -> bool:
    """Return True if path contains ardupilot directory."""
    return "ardupilot" in path.parts


def is_safe_repo_file(file_path: Path, repo_root: Path = REPO_ROOT) -> bool:
    """Check if file_path is safely contained within repo_root and not in ardupilot or git."""
    try:
        resolved = file_path.resolve()
        resolved.relative_to(repo_root.resolve())
        if is_ardupilot_path(resolved):
            return False
        if any(part.startswith(".git") for part in resolved.parts):
            return False
        return resolved.is_file()
    except (ValueError, RuntimeError):
        return False


def extract_title(content: str, fallback_name: str) -> str:
    """Extract first top-level Markdown title or fall back to cleaned filename."""
    match = re.search(r"^\s*#\s+(.+)$", content, re.MULTILINE)
    if match:
        raw_title = match.group(1).strip()
        cleaned = re.sub(r"[*_`]", "", raw_title)
        return cleaned
    stem = Path(fallback_name).stem
    return stem.replace("-", " ").replace("_", " ").title()


def determine_category(rel_path: str) -> str:
    """Determine document category for inventory display."""
    if rel_path in ("PLAN.md", "CONTEXT.md"):
        return "Core Architecture & Plans"
    if rel_path.startswith("docs/adr/"):
        return "Architecture Decision Records (ADRs)"
    if rel_path.startswith("hardware/bom/") or rel_path.startswith("docs/hardware/"):
        return "Hardware & BOM"
    if rel_path.startswith("docs/pilots/"):
        return "Pilots & Bring-Up"
    if rel_path.startswith("docs/agents/"):
        return "Agent Guides"
    return "Project Documentation"


def get_docs_inventory(repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """Scan and return the curated documentation subset via runtime glob.

    Never hardcoded: scanned from disk on each call.
    Never includes ardupilot/.
    """
    seen_paths: set[Path] = set()
    inventory: list[dict[str, Any]] = []

    for pattern in CURATED_GLOBS:
        for file_path in repo_root.glob(pattern):
            if not file_path.is_file():
                continue
            resolved = file_path.resolve()
            if resolved in seen_paths or is_ardupilot_path(resolved):
                continue
            seen_paths.add(resolved)

            rel_path = resolved.relative_to(repo_root.resolve()).as_posix()
            try:
                content = resolved.read_text(encoding="utf-8-sig")
            except Exception:
                content = ""

            title = extract_title(content, fallback_name=resolved.name)
            stat = resolved.stat()
            mtime_dt = datetime.datetime.fromtimestamp(stat.st_mtime)

            inventory.append(
                {
                    "rel_path": rel_path,
                    "title": title,
                    "category": determine_category(rel_path),
                    "is_adr": rel_path.startswith("docs/adr/"),
                    "size_bytes": stat.st_size,
                    "size_kb": round(stat.st_size / 1024, 1),
                    "mtime": mtime_dt.strftime("%Y-%m-%d %H:%M"),
                    "mtime_ts": stat.st_mtime,
                    "url": f"/docs/{rel_path}",
                }
            )

    # Sort deterministically: category, then title/filename
    inventory.sort(key=lambda d: (d["category"], d["rel_path"]))
    return inventory


def get_adr_inventory(repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """Return inventory of ADRs from docs/adr/*.md, sorted by number."""
    all_docs = get_docs_inventory(repo_root)
    adrs: list[dict[str, Any]] = []

    for doc in all_docs:
        if not doc["is_adr"]:
            continue
        rel = doc["rel_path"]
        filename = Path(rel).name
        # Match e.g. 0001 from 0001-open-hardware...
        m = re.match(r"^(\d+)", filename)
        num_str = m.group(1) if m else "0000"
        adrs.append(
            {
                **doc,
                "adr_num": num_str,
                "filename": filename,
            }
        )

    adrs.sort(key=lambda a: a["adr_num"])
    return adrs


class DocLinkRewriter(Treeprocessor):
    """Rewrite relative links and images in rendered markdown against disk locations.

    Flags broken links visibly in the HTML output.
    """

    def __init__(self, md: markdown.Markdown, repo_root: Path, source_file: Path):
        super().__init__(md)
        self.repo_root = repo_root.resolve()
        self.source_file = source_file.resolve()
        self.source_dir = self.source_file.parent

    def run(self, root: ET.Element) -> None:
        # Process hyperlinks
        for a in list(root.iter("a")):
            href = (a.attrib.get("href") or "").strip()
            if not href:
                continue

            parsed = urlparse(href)
            if parsed.scheme in ("http", "https", "mailto", "ftp"):
                a.attrib["target"] = "_blank"
                a.attrib["rel"] = "noopener noreferrer"
                continue

            if href.startswith("#"):
                continue

            path_part, sep, anchor = href.partition("#")
            anchor_suffix = f"#{anchor}" if sep else ""
            unquoted = unquote(path_part).strip()

            if not unquoted:
                continue

            # Resolve target on disk
            if unquoted.startswith("/docs/"):
                target = (self.repo_root / unquoted[6:].lstrip("/")).resolve()
            elif unquoted.startswith("/md/"):
                target = (self.repo_root / unquoted[4:].lstrip("/")).resolve()
            elif unquoted.startswith("/"):
                target = (self.repo_root / unquoted.lstrip("/")).resolve()
            else:
                target = (self.source_dir / unquoted).resolve()

            # Path safety check
            safe = is_safe_repo_file(target, self.repo_root)

            if not safe or not target.exists():
                classes = a.attrib.get("class", "").split()
                if "broken-link" not in classes:
                    classes.append("broken-link")
                a.attrib["class"] = " ".join(classes)
                a.attrib["title"] = f"Broken link: target '{href}' not found on disk"

                badge = ET.Element("span")
                badge.attrib["class"] = "badge-broken"
                badge.attrib["title"] = f"Missing target: {href}"
                badge.text = "broken"
                a.append(badge)
            else:
                rel_posix = target.relative_to(self.repo_root).as_posix()
                if target.suffix.lower() in (".md", ".markdown"):
                    a.attrib["href"] = f"/docs/{rel_posix}{anchor_suffix}"
                else:
                    a.attrib["href"] = f"/md/{rel_posix}{anchor_suffix}"

        # Process image tags
        for img in list(root.iter("img")):
            src = (img.attrib.get("src") or "").strip()
            if not src:
                continue

            parsed = urlparse(src)
            if parsed.scheme in ("http", "https", "data"):
                continue

            unquoted = unquote(src).strip()
            if unquoted.startswith("/md/"):
                target = (self.repo_root / unquoted[4:].lstrip("/")).resolve()
            elif unquoted.startswith("/"):
                target = (self.repo_root / unquoted.lstrip("/")).resolve()
            else:
                target = (self.source_dir / unquoted).resolve()

            safe = is_safe_repo_file(target, self.repo_root)

            if not safe or not target.exists():
                classes = img.attrib.get("class", "").split()
                if "broken-image" not in classes:
                    classes.append("broken-image")
                img.attrib["class"] = " ".join(classes)
                img.attrib["title"] = f"Broken image: '{src}' not found on disk"
                img.attrib["alt"] = f"[Broken image: {src}]"
            else:
                rel_posix = target.relative_to(self.repo_root).as_posix()
                img.attrib["src"] = f"/md/{rel_posix}"


def render_markdown_doc(source_file: Path, repo_root: Path = REPO_ROOT) -> tuple[str, str, str]:
    """Render markdown document to HTML with Pygments and link rewriting.

    Returns (html_content, table_of_contents_html, title).
    """
    raw_text = source_file.read_text(encoding="utf-8-sig")
    title = extract_title(raw_text, fallback_name=source_file.name)

    class LinkRewriterExtension(Extension):
        def extendMarkdown(self, md: markdown.Markdown) -> None:
            md.treeprocessors.register(
                DocLinkRewriter(md, repo_root, source_file),
                "doc_link_rewriter",
                15,
            )

    md = markdown.Markdown(
        extensions=[
            "wikilinks",
            "toc",
            "tables",
            "fenced_code",
            "codehilite",
            LinkRewriterExtension(),
        ],
        extension_configs={
            "codehilite": {
                "guess_lang": False,
                "css_class": "codehilite",
            },
            "toc": {
                "permalink": True,
            },
            "wikilinks": {
                "base_url": "/docs/",
                "end_url": "",
            },
        },
    )

    html_content = md.convert(raw_text)
    toc_html = getattr(md, "toc", "")
    return html_content, toc_html, title


@bp.route("/docs")
@bp.route("/docs/")
def docs_index() -> str:
    """Render inventory of curated docs subset. Supports search filtering."""
    query = request.args.get("q", "").strip()
    inventory = get_docs_inventory(REPO_ROOT)

    if query:
        q_lower = query.lower()
        filtered = [
            d
            for d in inventory
            if q_lower in d["title"].lower()
            or q_lower in d["rel_path"].lower()
            or q_lower in d["category"].lower()
        ]
    else:
        filtered = inventory

    # Group by category for structured display
    grouped: dict[str, list[dict[str, Any]]] = {}
    for doc in filtered:
        grouped.setdefault(doc["category"], []).append(doc)

    return render_template(
        "docs_index.html",
        docs=filtered,
        grouped_docs=grouped,
        query=query,
        is_adr=False,
        total_docs=len(inventory),
    )


@bp.route("/docs/adr")
@bp.route("/docs/adr/")
def adr_index() -> str:
    """ADR index page listing docs/adr/*.md with titles."""
    adrs = get_adr_inventory(REPO_ROOT)
    return render_template(
        "docs_index.html",
        adrs=adrs,
        is_adr=True,
        total_adrs=len(adrs),
    )


@bp.route("/docs/<path:doc_path>")
def docs_page(doc_path: str) -> str:
    """Render a curated markdown document."""
    cleaned_path = doc_path.strip().lstrip("/\\")

    # Guard against path traversal
    candidate = (REPO_ROOT / cleaned_path).resolve()

    # If not found directly, check docs/<cleaned_path> (e.g. adr/0001-... -> docs/adr/0001-...)
    if not candidate.is_file():
        alt = (REPO_ROOT / "docs" / cleaned_path).resolve()
        if alt.is_file():
            candidate = alt

    # Safety checks
    if not is_safe_repo_file(candidate, REPO_ROOT):
        abort(404, description=f"Document not found or forbidden: {doc_path}")

    # Must be in the curated inventory
    inventory = get_docs_inventory(REPO_ROOT)
    curated_paths = {d["rel_path"] for d in inventory}
    rel_posix = candidate.relative_to(REPO_ROOT.resolve()).as_posix()

    if rel_posix not in curated_paths:
        abort(404, description=f"File is outside the curated documentation subset: {doc_path}")

    html_content, toc_html, title = render_markdown_doc(candidate, REPO_ROOT)
    stat = candidate.stat()
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")

    return render_template(
        "docs_page.html",
        content=html_content,
        toc=toc_html,
        title=title,
        doc_path=rel_posix,
        size_kb=round(stat.st_size / 1024, 1),
        mtime=mtime,
    )


@bp.route("/md/<path:asset_path>")
def raw_asset(asset_path: str):
    """Serve raw workspace assets (images, attachments) referenced by docs."""
    cleaned = asset_path.strip().lstrip("/\\")
    candidate = (REPO_ROOT / cleaned).resolve()

    # Same path-safety rules
    if not is_safe_repo_file(candidate, REPO_ROOT):
        abort(404, description=f"Asset not found or access forbidden: {asset_path}")

    return send_file(candidate)

"""Flask application factory for Follow-up App v1.

Registers dashboard routes and auto-discovers candidate feature blueprints
(docs, progress, github_issues) in a tolerant loop.
"""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any

from flask import Flask, render_template

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure the Follow-up App Flask instance."""
    web_dir = Path(__file__).resolve().parent

    app = Flask(
        __name__,
        static_folder=str(web_dir / "static"),
        static_url_path="/static",
        template_folder=str(web_dir / "templates"),
    )

    app.config.from_mapping(
        SECRET_KEY="madpilot-local-workspace-key",
        REPO_ROOT=REPO_ROOT,
    )

    if test_config:
        app.config.from_mapping(test_config)

    # Tolerant feature blueprint discovery loop
    # Candidate modules: docs, progress, github_issues
    candidate_features = ["docs", "progress", "github_issues"]
    active_features: dict[str, dict[str, Any]] = {}

    for feature in candidate_features:
        try:
            mod = importlib.import_module(f"web.{feature}")
            if hasattr(mod, "bp"):
                app.register_blueprint(mod.bp)
                active_features[feature] = {
                    "available": True,
                    "module": mod,
                    "error": None,
                }
                logger.info("Registered blueprint for feature '%s'", feature)
            else:
                active_features[feature] = {
                    "available": False,
                    "module": None,
                    "error": "No 'bp' blueprint attribute found",
                }
        except ModuleNotFoundError as exc:
            # Expected when other lanes have not yet created their module
            if exc.name in (f"web.{feature}", feature):
                active_features[feature] = {
                    "available": False,
                    "module": None,
                    "error": "Feature module not yet built",
                }
            else:
                active_features[feature] = {
                    "available": False,
                    "module": None,
                    "error": f"Missing dependency in '{feature}': {exc}",
                }
        except Exception as exc:
            logger.warning("Failed to load feature '%s': %s", feature, exc)
            active_features[feature] = {
                "available": False,
                "module": None,
                "error": str(exc),
            }

    app.config["ACTIVE_FEATURES"] = active_features

    @app.context_processor
    def inject_context() -> dict[str, Any]:
        """Inject feature availability and repo details into all templates."""
        return {
            "features": app.config.get("ACTIVE_FEATURES", {}),
            "repo_root": REPO_ROOT,
        }

    @app.route("/")
    def index() -> str:
        """Dashboard overview: links to Docs, Progress, and Issues."""
        features = app.config.get("ACTIVE_FEATURES", {})
        docs_mod = features.get("docs", {}).get("module")

        docs_count = 0
        adr_count = 0
        recent_docs: list[dict[str, Any]] = []

        if docs_mod and hasattr(docs_mod, "get_docs_inventory"):
            inventory = docs_mod.get_docs_inventory()
            docs_count = len(inventory)
            adr_count = sum(1 for d in inventory if d.get("is_adr"))
            recent_docs = sorted(
                inventory,
                key=lambda d: d.get("mtime_ts", 0),
                reverse=True,
            )[:6]

        return render_template(
            "index.html",
            docs_count=docs_count,
            adr_count=adr_count,
            recent_docs=recent_docs,
        )

    return app

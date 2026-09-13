"""Entrypoint for python -m web."""

import os
from web.server import create_app


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8765"))
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")

    app = create_app()
    print(f"MADpilot Follow-up App running on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()

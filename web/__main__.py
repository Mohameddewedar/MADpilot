"""Entrypoint for python -m web."""

import os
import socket
from web.server import create_app


def _describe_urls(host: str, port: int) -> str:
    if host != "0.0.0.0":
        return f"http://{host}:{port}"
    lan_ip = None
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe.connect(("10.255.255.255", 1))
            lan_ip = probe.getsockname()[0]
        finally:
            probe.close()
    except OSError:
        pass
    urls = [f"http://127.0.0.1:{port}"]
    if lan_ip and not lan_ip.startswith("127."):
        urls.append(f"http://{lan_ip}:{port} (local network devices)")
    return " | ".join(urls)


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8765"))
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")

    app = create_app()
    print(f"MADpilot Follow-up App running on {_describe_urls(host, port)}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()

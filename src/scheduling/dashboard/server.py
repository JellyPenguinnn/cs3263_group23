"""Loopback-only HTTP transport. No arbitrary file serving or browser credentials."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # Keep private run identifiers out of HTTP logs.

    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def respond(self, status, data, content_type="application/json; charset=utf-8"):
        body = (
            data
            if isinstance(data, bytes)
            else json.dumps(data, allow_nan=False).encode()
        )
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
        )
        self.end_headers()
        self.wfile.write(body)

    def trusted(self):
        authority = f"127.0.0.1:{self.server.server_port}"
        return (
            self.headers.get("Host") == authority
            and self.headers.get("Sec-Fetch-Site") not in ("cross-site",)
            and self.headers.get("Origin", "http://" + authority)
            == "http://" + authority
        )

    def do_GET(self):
        from scheduling.dashboard.service import BusyError

        if not self.trusted():
            self.respond(403, {"error": "Use the local dashboard URL"})
            return
        parsed = urlsplit(self.path)
        if parsed.path in ASSETS:
            name, mime = ASSETS[parsed.path]
            self.respond(
                200,
                files("scheduling.dashboard").joinpath("static", name).read_bytes(),
                mime,
            )
            return
        args = {k: v[-1] for k, v in parse_qs(parsed.query).items()}
        app = self.server.app
        try:
            if parsed.path == "/api/session":
                result = app.bootstrap()
            elif parsed.path == "/api/run":
                result = app.overview(args["run"])
            elif parsed.path == "/api/cases":
                offset = int(args.get("offset", 0))
                if offset < 0:
                    raise ValueError("Invalid page")
                result = app.case_page(
                    args["run"],
                    query=args.get("q", ""),
                    task=args.get("task", ""),
                    outcome=args.get("outcome", ""),
                    offset=offset,
                    kind=args.get("kind", "controlled"),
                    variant=args.get("variant", "canonical"),
                    repeat=int(args.get("repeat", 0)),
                )
            elif parsed.path == "/api/case":
                result = app.case_detail(
                    args["run"],
                    int(args["id"]),
                    args.get("variant", "canonical"),
                    int(args.get("repeat", 0)),
                )
            else:
                self.respond(404, {"error": "Not found"})
                return
            self.respond(200, result)
        except BusyError:
            self.respond(409, {"error": "Records are updating. Refreshing shortly."})
        except (OSError, ValueError, KeyError, TypeError, LookupError):
            self.respond(
                422,
                {
                    "error": "Run unavailable or record integrity check failed. No results were substituted."
                },
            )

    def do_POST(self):
        self.respond(
            405, {"error": "Read-only dashboard. Start runs from the terminal."}
        )

    do_PUT = do_POST
    do_PATCH = do_POST
    do_DELETE = do_POST


def serve(args):
    from scheduling.dashboard.service import Dashboard

    app = Dashboard(args.runs_dir, run_dir=args.run_dir)
    if not 0 <= args.port <= 65535:
        raise ValueError("Invalid port")
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        server.app = app
        print(f"Dashboard: http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


def add_command(commands):
    parser = commands.add_parser(
        "dashboard",
        help="Read-only live monitor, results and validated case explorer",
    )
    parser.add_argument("--runs-dir", type=Path, default=Path("runs"))
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="Initially selected saved or running evaluation directory",
    )
    parser.add_argument("--port", type=int, default=8765)

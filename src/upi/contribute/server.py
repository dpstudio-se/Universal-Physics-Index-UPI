"""HTTP UI and JSON API for live UPI contributions."""

from __future__ import annotations

import json
import os
import queue
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from .service import ContributionError, ContributionService
from .store import ContributionStore

STATIC_DIR = Path(__file__).resolve().parent / "static"
PROMPT_FILE = STATIC_DIR / "upi-remote-indexer.system.md"
MAX_READ = 256_000
MAX_BATCH_READ = 1_000_000


class RateLimiter:
    """Fixed-window POST limiter per client address."""

    def __init__(self, max_hits: int = 30, window_s: float = 60.0):
        self.max_hits = max_hits
        self.window_s = window_s
        self._hits: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def allow(self, client: str) -> bool:
        now = time.time()
        with self._lock:
            stamps = [stamp for stamp in self._hits.get(client, []) if now - stamp < self.window_s]
            if len(stamps) >= self.max_hits:
                self._hits[client] = stamps
                return False
            stamps.append(now)
            self._hits[client] = stamps
            return True


class ContributionApp:
    """In-process app state for the contribution server."""

    def __init__(
        self,
        service: ContributionService,
        data_root: Path | None = None,
        review_token: str = "",
    ):
        self.service = service
        self.data_root = data_root or Path("data")
        self.review_token = review_token
        self.limiter = RateLimiter()
        self.subscribers: list[queue.Queue[dict[str, Any]]] = []
        self._sub_lock = threading.Lock()

    def publish(self, event: dict[str, Any]) -> None:
        with self._sub_lock:
            listeners = list(self.subscribers)
        for listener in listeners:
            try:
                listener.put_nowait(event)
            except queue.Full:
                continue

    def subscribe(self) -> queue.Queue[dict[str, Any]]:
        listener: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=64)
        with self._sub_lock:
            self.subscribers.append(listener)
        return listener

    def unsubscribe(self, listener: queue.Queue[dict[str, Any]]) -> None:
        with self._sub_lock:
            if listener in self.subscribers:
                self.subscribers.remove(listener)


def make_handler(app: ContributionApp):
    """Return a request handler bound to *app*."""

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = unquote(parsed.path)
            if path == "/":
                self._static("index.html", "text/html; charset=utf-8")
                return
            if path.startswith("/static/"):
                self._static(path.removeprefix("/static/"))
                return
            if path == "/api/health":
                self._json(200, {"ok": True, "verification_type": "software_test"})
                return
            if path == "/api/nodes":
                query = parse_qs(parsed.query)
                q = query.get("q", [None])[0]
                status = query.get("status", [None])[0]
                self._json(200, {"nodes": app.service.list_nodes(query=q, status=status)})
                return
            if path == "/api/graph":
                from upi.index import export_graph, load_graph

                graph = load_graph(app.data_root)
                self._json(200, export_graph(graph))
                return
            if path == "/api/hypotheses":
                from upi.index import hypothesis_registry

                self._json(
                    200,
                    {
                        "hypotheses": hypothesis_registry(app.data_root),
                        "verification_type": "software_test",
                    },
                )
                return
            if path == "/api/conflicts":
                from upi.debug import generate_debug_report

                report = generate_debug_report(app.data_root, inspect=True)
                self._json(
                    200,
                    {
                        "inspector": report.get("inspector"),
                        "findings": report.get("findings"),
                        "verification_type": "software_test",
                    },
                )
                return
            if path.startswith("/api/nodes/"):
                address = unquote(path.removeprefix("/api/nodes/"))
                node = app.service.get_node(address)
                if node is None:
                    self._json(404, {"errors": ["not found"]})
                    return
                self._json(200, node)
                return
            if path == "/api/events":
                self._sse(parse_qs(parsed.query))
                return
            if path in {"/prompt", "/api/system-prompt"}:
                self._prompt()
                return
            self._json(404, {"errors": ["unknown path"]})

        def do_POST(self) -> None:
            client = self.client_address[0] if self.client_address else "unknown"
            if not app.limiter.allow(client):
                self._json(429, {"errors": ["rate limit"]})
                return
            parsed = urlparse(self.path)
            if parsed.path == "/api/promote":
                payload = self._read_json(MAX_READ)
                if payload is None:
                    return
                try:
                    stored = app.service.promote(
                        str(payload.get("address") or ""),
                        str(self.headers.get("X-UPI-Review-Token") or ""),
                        app.review_token,
                    )
                except ContributionError as exc:
                    self._json(exc.status_code, {"errors": exc.errors})
                    return
                self._published(stored.address)
                promoted = app.service.get_node(stored.address)
                if promoted is None:
                    self._json(500, {"errors": ["missing after promote"]})
                    return
                self._json(200, promoted)
                return
            if parsed.path == "/api/merge-check":
                from upi.merge import merge_from_live

                pack = merge_from_live(app.service, app.data_root)
                self._json(200, pack)
                return
            if parsed.path == "/api/ingest":
                self._ingest(parse_qs(parsed.query))
                return
            if parsed.path != "/api/nodes":
                self._json(404, {"errors": ["unknown path"]})
                return
            payload = self._read_json(MAX_READ)
            if payload is None:
                return
            try:
                stored = app.service.submit(payload)
            except ContributionError as exc:
                self._json(exc.status_code, {"errors": exc.errors})
                return
            self._published(stored.address)
            created = app.service.get_node(stored.address)
            if created is None:
                self._json(500, {"errors": ["missing after insert"]})
                return
            self._json(201, created)

        def _ingest(self, query: dict[str, list[str]]) -> None:
            mode = (query.get("mode") or ["check"])[0]
            if mode not in {"check", "insert"}:
                self._json(400, {"errors": ["mode must be check or insert"]})
                return
            payload = self._read_json(MAX_BATCH_READ)
            if payload is None:
                return
            if mode == "check":
                report = app.service.check_batch(payload)
                self._json(200 if report["ok"] else 400, report)
                return
            report = app.service.insert_batch(payload)
            for record in report["records"]:
                if record.get("inserted"):
                    self._published(str(record.get("address") or ""))
            code = 200 if report["ok"] else 400
            if report["inserted"] and not report["ok"]:
                code = 207
            self._json(code, report)

        def _read_json(self, limit: int) -> dict[str, Any] | None:
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > limit:
                self._json(400, {"errors": ["invalid Content-Length"]})
                return None
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError):
                self._json(400, {"errors": ["invalid JSON"]})
                return None
            if not isinstance(payload, dict):
                self._json(400, {"errors": ["JSON object required"]})
                return None
            return payload

        def _published(self, address: str) -> None:
            node = app.service.get_node(address)
            if node is None:
                return
            app.publish(
                {
                    "kind": "contribution",
                    "address": node["address"],
                    "title": node["title"],
                    "status": node["status"],
                    "created_at": node["created_at"],
                }
            )

        def _prompt(self) -> None:
            if not PROMPT_FILE.is_file():
                self._json(404, {"errors": ["system prompt missing"]})
                return
            data = PROMPT_FILE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header(
                "Content-Disposition",
                'attachment; filename="upi-remote-indexer.system.md"',
            )
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _sse(self, query: dict[str, list[str]]) -> None:
            last_id = 0
            if "last_id" in query:
                try:
                    last_id = int(query["last_id"][0])
                except ValueError:
                    last_id = 0
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            for event in app.service.store.events_since(last_id):
                self._write_sse(event)
            listener = app.subscribe()
            try:
                while True:
                    try:
                        event = listener.get(timeout=15)
                    except queue.Empty:
                        self.wfile.write(b": keepalive\n\n")
                        self.wfile.flush()
                        continue
                    self._write_sse(event)
            except (BrokenPipeError, ConnectionResetError, OSError):
                return
            finally:
                app.unsubscribe(listener)

        def _write_sse(self, event: dict[str, Any]) -> None:
            self.wfile.write(b"data: " + json.dumps(event).encode("utf-8") + b"\n\n")
            self.wfile.flush()

        def _static(self, name: str, content_type: str | None = None) -> None:
            safe = Path(name).name
            path = STATIC_DIR / safe
            if not path.is_file():
                self._json(404, {"errors": ["missing static file"]})
                return
            data = path.read_bytes()
            types = {
                ".html": "text/html; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".js": "text/javascript; charset=utf-8",
            }
            self.send_response(200)
            self.send_header("Content-Type", content_type or types.get(path.suffix, "application/octet-stream"))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _json(self, code: int, body: dict[str, Any]) -> None:
            raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

    return Handler


def serve(
    host: str = "127.0.0.1",
    port: int = 8080,
    database: str | None = None,
    data_root: Path | None = None,
) -> None:
    """Start the contribution UI until interrupted."""
    database = database or os.environ.get("UPI_DATABASE_URL") or "sqlite:///upi.db"
    store = ContributionStore(database)
    service = ContributionService(store)
    service.seed()
    if data_root is None:
        data_root = Path("data")
    loaded = service.load_repo_records(data_root)
    app = ContributionApp(
        service,
        data_root=data_root,
        review_token=os.environ.get("UPI_REVIEW_TOKEN", ""),
    )
    handler = make_handler(app)
    httpd = ThreadingHTTPServer((host, port), handler)
    print(f"UPI contribution UI on http://{host}:{port}/")
    print(f"Database: {database}")
    print(f"Loaded repo records: {loaded}")
    print("dna_minne_7.834 seeded. verification_type=software_test")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping")
    finally:
        httpd.server_close()
        store.close()

"""Discovery layer for any AI/AGI/ASI/LLM: manifest, llms.txt and HTTP routes."""

from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

from upi.contribute.server import ContributionApp, make_handler
from upi.contribute.service import PUBLIC_STATUSES, ContributionService
from upi.contribute.store import ContributionStore
from upi.remote import GUARDRAILS, remote_manifest, render_llms_txt

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_forbids_est_and_matches_service_policy() -> None:
    manifest = remote_manifest()
    assert manifest["verification_type"] == "software_test"
    assert manifest["claims_experimental_verification"] is False
    policy = manifest["status_policy"]
    assert "EST" in policy["forbidden_for_models"]
    assert set(policy["allowed_for_models"]) == PUBLIC_STATUSES
    assert any("EST" in rule for rule in GUARDRAILS)


def test_manifest_references_existing_files() -> None:
    manifest = remote_manifest()
    paths = [
        manifest["batch"]["schema"],
        manifest["batch"]["example"],
        manifest["research_mode"]["master_prompt"],
        *manifest["docs"].values(),
    ]
    for rel in paths:
        assert (ROOT / rel).is_file(), rel


def test_root_llms_txt_is_in_sync() -> None:
    text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert text.replace("\r\n", "\n") == render_llms_txt()


def test_http_remote_routes() -> None:
    service = ContributionService(ContributionStore("sqlite:///:memory:"))
    service.seed()
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(ContributionApp(service)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    base = f"http://{host}:{port}"
    try:
        with urlopen(f"{base}/api/remote", timeout=2) as response:
            assert json.load(response)["flow"].startswith("MODEL")
        with urlopen(f"{base}/.well-known/upi-remote.json", timeout=2) as response:
            assert json.load(response)["remote_version"]
        with urlopen(f"{base}/llms.txt", timeout=2) as response:
            assert response.headers["Content-Type"].startswith("text/plain")
            assert "Never assign EST" in response.read().decode("utf-8")
    finally:
        server.shutdown()
        server.server_close()

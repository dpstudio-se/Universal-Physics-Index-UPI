"""verification_type: software_test; local HTTP contract, not public deployment."""

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from upi.contribute.server import ContributionApp, make_handler
from upi.contribute.service import ContributionService
from upi.contribute.store import ContributionStore


def test_foundation_http_is_bounded_and_does_not_execute():
    store = ContributionStore("sqlite:///:memory:")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(ContributionApp(ContributionService(store)))
    )
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        for path in ("/foundation/", "/foundation/foundation.js", "/foundation/foundation.css"):
            with urlopen(base + path, timeout=3) as response:
                assert response.status == 200
        body = {
            "operation": "derive",
            "source": "frequency",
            "target": "mass_equivalent",
            "value": 8,
            "unit": "Hz",
            "method": "cch",
        }
        with urlopen(
            Request(
                base + "/api/foundation",
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"},
            ),
            timeout=3,
        ) as response:
            result = json.load(response)
        assert result["status"] == "DER" and len(result["trace"]) == 2
        for invalid in (
            {"operation": "execute", "code": "print(1)"},
            {**body, "unit": "kg"},
            {"operation": "triangle", "generation": 9999},
        ):
            with pytest.raises(HTTPError) as exc:
                urlopen(
                    Request(base + "/api/foundation", data=json.dumps(invalid).encode()), timeout=3
                )
            assert exc.value.code == 400
            exc.value.close()
    finally:
        server.shutdown()
        worker.join(timeout=3)
        server.server_close()
        store.close()

"""verification_type: software_test; HTTP behavior, not deployment evidence."""

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from upi.contribute.server import ContributionApp, make_handler
from upi.contribute.service import ContributionService
from upi.contribute.store import ContributionStore
from upi.knot_examples import example_document
from upi.knot_io import dumps


def test_knot_routes_and_analysis():
    store = ContributionStore("sqlite:///:memory:")
    server = ThreadingHTTPServer(("127.0.0.1", 0),
                                make_handler(ContributionApp(ContributionService(store))))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        for path in ("/oden", "/oden/oden.css", "/oden/oden.js", "/oden/knots.json",
                     "/oden/paths.example.json", "/api/knots"):
            with urlopen(base + path, timeout=3) as response:
                assert response.status == 200
        request = Request(base + "/api/knots/analyze", data=dumps(example_document()).encode(),
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=3) as response:
            report = json.load(response)
        assert report["knots"][0]["state"] == "CLOSED"
        assert report["knots"][1]["state"] == "OPEN"
        with pytest.raises(HTTPError) as error:
            urlopen(Request(base + "/api/knots/analyze", data=b'{"format":"bad"}'), timeout=3)
        assert error.value.code == 400
        error.value.close()
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()
        store.close()

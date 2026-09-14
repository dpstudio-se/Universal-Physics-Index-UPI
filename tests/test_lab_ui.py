"""verification_type: software_test; HTTP delivery, not visual rendering."""

import threading
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from upi.contribute.server import ContributionApp, make_handler
from upi.contribute.service import ContributionService
from upi.contribute.store import ContributionStore


def test_lab_routes_and_assets_are_served():
    store = ContributionStore("sqlite:///:memory:")
    app = ContributionApp(ContributionService(store))
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        for path, mime, expected in (
            ("/lab", "text/html", 'id="lab-form"'),
            ("/lab/", "text/html", 'lang="sv"'),
            ("/static/lab.css", "text/css", "@media"),
            ("/static/lab-math.js", "text/javascript", "calculate"),
            ("/static/lab.js", "text/javascript", "createObjectURL"),
            ("/", "text/html", 'href="/lab"'),
        ):
            with urlopen(f"http://{host}:{port}{path}", timeout=3) as response:
                assert response.status == 200
                assert response.headers.get_content_type() == mime
                assert expected in response.read().decode("utf-8")
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()
        store.close()

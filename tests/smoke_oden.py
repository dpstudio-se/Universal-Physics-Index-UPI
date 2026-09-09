"""Optional real-browser verification_type: software_test. Requires Playwright + Edge."""

import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

from upi.contribute.server import ContributionApp, make_handler
from upi.contribute.service import ContributionService
from upi.contribute.store import ContributionStore
from upi.knot_examples import example_document
from upi.knot_io import dumps
from upi.knot_site import build


def main():
    output = Path("dist/oden").resolve()
    build(output)
    server = ThreadingHTTPServer(("127.0.0.1", 0),
                                partial(SimpleHTTPRequestHandler, directory=str(output)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    errors = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            print("Browser:", browser.version)
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console", lambda message: errors.append(message.text)
                    if message.type == "error" else None)
            page.goto(f"http://127.0.0.1:{server.server_port}/")
            page.wait_for_selector(".knot-row")
            assert page.locator(".knot-row").count() == 7
            page.get_by_role("button", name="observer-offset: OPEN", exact=True).click()
            assert "0.762" in page.locator(".epsilon").inner_text()
            page.locator("#filter-state").select_option("CLOSED")
            assert page.locator(".knot-row").count() == 1
            page.locator("#filter-state").select_option("")
            for name, value, count in [("time", "1690", 1), ("domain", "history", 1),
                                       ("type", "INFORMATION_LOSS", 1), ("source", "absent", 0),
                                       ("score", "0.5", 0), ("confidence", "1", 0)]:
                page.locator("#filter-" + name).fill(value)
                assert page.locator(".knot-row").count() == count
                page.locator("#filter-" + name).fill("0" if name in {"score", "confidence"} else "")
            with page.expect_download() as download:
                page.locator("#export").click()
            assert download.value.suggested_filename == "oden-knots.json"
            page.locator("#import").set_input_files(str(output / "knots.json"))
            assert page.locator(".knot-row").count() == 7
            for width in (1440, 390):
                page.set_viewport_size({"width": width, "height": 1000})
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                page.screenshot(path=str(output.parent / f"oden-{width}.png"), full_page=True)
            malicious = json.loads((output / "knots.json").read_text(encoding="utf-8"))
            malicious["knots"][0]["a"]["observation"]["name"] = '<img src=x onerror="window.pwned=1">'
            page.locator("#import").set_input_files({"name": "untrusted.json", "mimeType": "application/json",
                                                     "buffer": json.dumps(malicious).encode()})
            assert page.evaluate("window.pwned === undefined")
            store = ContributionStore("sqlite:///:memory:")
            api = ThreadingHTTPServer(("127.0.0.1", 0),
                                     make_handler(ContributionApp(ContributionService(store))))
            api_thread = threading.Thread(target=api.serve_forever, daemon=True)
            api_thread.start()
            try:
                page.goto(f"http://127.0.0.1:{api.server_port}/oden")
                page.wait_for_selector(".knot-row")
                page.locator(".analyze summary").click()
                page.locator("#input").fill(dumps(example_document()))
                page.locator("#analyze").click()
                page.wait_for_function("document.querySelectorAll('.knot-row').length === 2")
                assert "Analyzed supplied paths" in page.locator("#message").inner_text()
            finally:
                api.shutdown()
                api_thread.join(timeout=3)
                api.server_close()
                store.close()
            assert not errors, errors
            browser.close()
        print("PASS: desktop/mobile, selection, all filters, import/export, inert text, live analysis")
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


if __name__ == "__main__":
    main()

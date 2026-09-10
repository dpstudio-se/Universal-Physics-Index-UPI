"""Optional Edge rendering check. verification_type: software_test."""

import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    root = Path("dist/tf").resolve()
    server = ThreadingHTTPServer(("127.0.0.1", 0),
                                partial(SimpleHTTPRequestHandler, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    errors = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.goto(f"http://127.0.0.1:{server.server_port}/")
            assert page.locator("details").count() == 193
            page.get_by_text("TF 7:16 ·", exact=False).first.click()
            assert "grov oaktsamhet" in page.locator("details[open] blockquote").inner_text()
            for width in (1440, 390):
                page.set_viewport_size({"width": width, "height": 900})
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                page.screenshot(path=str(root / f"preview-{width}.png"))
            assert not errors, errors
            browser.close()
        print("PASS: 193 provisions, complete TF 7:16, 1440/390px, no console errors")
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


if __name__ == "__main__":
    main()

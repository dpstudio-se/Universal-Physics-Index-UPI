"""Optional Edge UI control. verification_type: software_test."""

import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from upi.contribute.server import ContributionApp, make_handler
from upi.contribute.service import ContributionService
from upi.contribute.store import ContributionStore


def main():
    store = ContributionStore("sqlite:///:memory:")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(ContributionApp(ContributionService(store)))
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    errors = []
    out = Path("dist/foundation-preview")
    out.mkdir(exist_ok=True, parents=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda e: errors.append(e.text) if e.type == "error" else None)
            page.goto(f"http://127.0.0.1:{server.server_port}/foundation/")
            page.locator("#derive button").click()
            expect(page.locator("#trace li")).to_have_count(2)
            page.locator("#derive select[name=target]").select_option("dark_matter_particle")
            page.locator("#derive button").click()
            expect(page.locator("#derive-result")).to_contain_text("STOP")
            page.locator("#analog-run").click()
            expect(page.locator("#analog-result")).to_contain_text("MISFIT")
            page.locator("#rf button").click()
            expect(page.locator("#rf-result")).to_contain_text("FSPL")
            page.locator("#stub button").click()
            expect(page.locator("#stub-result")).to_contain_text("VSWR = 1")
            page.locator("#stub select[name=load]").select_option("0")
            page.locator("#stub button").click()
            expect(page.locator("#stub-result")).to_contain_text("ej ändlig")
            page.locator("#geo-run").click()
            expect(page.locator("#geo-result .layer")).to_have_count(9)
            page.locator("#triangle button").click()
            expect(page.locator("#triangle-result")).to_contain_text("121")
            for width in (1440, 390):
                page.set_viewport_size({"width": width, "height": 900})
                page.evaluate("scrollTo(0,0)")
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                page.screenshot(path=str(out / f"preview-{width}.png"), full_page=True)
            assert not errors, errors
            browser.close()
        print(
            "PASS: six panels, hypothesis STOP, analog MISFIT, matched/open controls, 9 layers, 1440/390px, no console errors"
        )
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()
        store.close()


if __name__ == "__main__":
    main()

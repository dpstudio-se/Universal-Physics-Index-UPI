#!/usr/bin/env python3
"""Read-only UPI audit helper for external social-media source material.

Purpose
-------
Social posts (X/Twitter, etc.) referenced in UPI research discussions are
external, self-published material. They can be quoted for context, but they
are never independent scientific evidence and must never be silently
promoted to EST/DER status.

This tool does not scrape or render JavaScript-heavy pages itself (that
requires a browser runtime that is not assumed to be available in CI). It
instead classifies a *snapshot* of the page/post text that was already
captured (for example via a browser tool, screenshot transcription, or a
manual copy/paste) and emits a structured, typed report using UPI's
evidence-classification vocabulary.

TF1766 note: this helper is transparency/audit-only. It exposes and
classifies claims found in the snapshot; it never bypasses higher-priority
policy, security, permission, or scientific-status gates, and it never
merges, approves, or promotes canonical scientific status on its own.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlparse

if hasattr(sys.stdout, "reconfigure"):
    # Console code pages (e.g. Windows cp1252) can't render every Unicode
    # symbol found in social-media handles/bios (Om, Omega, phi, ...).
    # Replace instead of crashing so the audit output is usable everywhere.
    sys.stdout.reconfigure(errors="replace")

ALLOWED_STATUS = {"EST", "DER", "HYP", "STOP", "ERR", "SYM"}

# Language that, if found in a social-media snapshot, must never be read as
# established fact without independent, cited, out-of-band evidence.
RISK_TERMS = (
    "proof",
    "proven",
    "solved",
    "independent",
    "verification",
    "verified",
    "evidence",
    "resonance",
    "universal",
    "causal",
    "physical proof",
    "breakthrough",
)


@dataclass
class SocialSourceReport:
    source_url: str
    host: str
    account_handle: str
    snapshot_path: str
    snapshot_chars: int
    excerpt: str
    risk_flags: list[str]
    status_mentions: list[str]
    classification: str
    evidence_boundary: str
    next_actions: list[str]
    tf1766_audit: dict[str, str | bool]


def account_handle_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    return path.split("/")[0] if path else ""


def scan_terms(text: str, terms: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return sorted({t for t in terms if t in lowered})


def status_mentions(text: str) -> list[str]:
    upper = text.upper()
    return sorted({s for s in ALLOWED_STATUS if re.search(rf"\b{re.escape(s)}\b", upper)})


def tf1766_classify(risk_flags: list[str]) -> dict[str, str | bool]:
    action = "REVIEW" if risk_flags else "CONTINUE"
    return {
        "transparent": True,
        "reason_exposed": True,
        "classification_verified": False,
        "override": False,
        "next_action": action,
        "rule_id": "TF1766-AUDIT-V1",
    }


def build_report(url: str, snapshot_path: Path) -> SocialSourceReport:
    text = snapshot_path.read_text(encoding="utf-8", errors="replace")
    risk_flags = scan_terms(text, RISK_TERMS)
    excerpt = " ".join(text.split())[:600]
    return SocialSourceReport(
        source_url=url,
        host=urlparse(url).netloc,
        account_handle=account_handle_from_url(url),
        snapshot_path=str(snapshot_path),
        snapshot_chars=len(text),
        excerpt=excerpt,
        risk_flags=risk_flags,
        status_mentions=status_mentions(text),
        classification="SYM",
        evidence_boundary=(
            "Self-published social-media content is symbolic/self-authored "
            "(SYM) source material only. It documents that a claim or image "
            "was posted by the account, not that any physical or "
            "mathematical claim within it is established. Promotion to "
            "EST/DER requires independent, cited, out-of-band evidence."
        ),
        next_actions=[
            "Do not cite this snapshot as EST/DER evidence on its own.",
            "If a specific claim recurs, trace it to a primary source with "
            "data, code, or a reproducible derivation.",
            "Keep unresolved claims tagged HYP or STOP per repo convention.",
        ],
        tf1766_audit=tf1766_classify(risk_flags),
    )


def print_report(r: SocialSourceReport) -> None:
    print(f"UPI Social Source Audit: {r.source_url}")
    print(f"account: @{r.account_handle}  host: {r.host}  snapshot: {r.snapshot_path}")
    print(f"classification: {r.classification}")
    print("\nEXCERPT")
    print(r.excerpt or "(empty snapshot)")
    print(f"\nRISK FLAGS: {', '.join(r.risk_flags) or 'none'}")
    print(f"STATUS MENTIONS: {', '.join(r.status_mentions) or 'none'}")
    print("\nEVIDENCE BOUNDARY")
    print(r.evidence_boundary)
    print("\nNEXT ACTIONS")
    for x in r.next_actions:
        print(f"- {x}")
    print("\nTF1766 AUDIT")
    print(json.dumps(r.tf1766_audit, indent=2, ensure_ascii=False))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True, help="Source URL, e.g. https://x.com/handle")
    ap.add_argument(
        "--snapshot",
        required=True,
        help="Path to a previously captured text/HTML snapshot of the page or post.",
    )
    ap.add_argument("--json", dest="json_path", help="Optional path to write the JSON report.")
    args = ap.parse_args()

    snapshot_path = Path(args.snapshot)
    if not snapshot_path.is_file():
        print(f"ERROR: snapshot file not found: {snapshot_path}", file=sys.stderr)
        return 2

    report = build_report(args.url, snapshot_path)
    if args.json_path:
        Path(args.json_path).write_text(
            json.dumps(asdict(report), indent=2, ensure_ascii=False), encoding="utf-8"
        )
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

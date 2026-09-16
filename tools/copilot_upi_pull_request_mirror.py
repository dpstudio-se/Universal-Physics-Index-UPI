#!/usr/bin/env python3
"""Read-only Copilot helper for auditing UPI pull requests.

The tool analyzes pull requests through the GitHub CLI (`gh`) and produces a
machine-readable mirror-loop report. It never merges, approves, promotes
scientific status, or rewrites repository data.

Usage:
  python tools/copilot_upi_pull_request_mirror.py --repo dpstudio-se/Universal-Physics-Index-UPI
  python tools/copilot_upi_pull_request_mirror.py --repo dpstudio-se/Universal-Physics-Index-UPI --pr 24
  python tools/copilot_upi_pull_request_mirror.py --repo dpstudio-se/Universal-Physics-Index-UPI --all-open --json report.json

Required: GitHub CLI (`gh`) authenticated for the target repository.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ALLOWED_STATUS = {"EST", "DER", "HYP", "STOP", "ERR", "SYM"}
RISK_TERMS = (
    "promote",
    "promotion",
    "physical proof",
    "causal",
    "resonance",
    "universal",
    "solved",
    "independent",
    "verification",
    "evidence",
    "frequency",
    "mass",
    "hodge",
    "riemann",
    "yang-mills",
    "navier-stokes",
    "p vs np",
    "birch",
)


@dataclass
class Gate:
    name: str
    state: str
    detail: str


@dataclass
class MirrorReport:
    repository: str
    pr: int
    title: str
    url: str
    head: str
    base: str
    draft: bool
    gates: list[Gate]
    changed_files: list[str]
    risk_flags: list[str]
    status_mentions: list[str]
    evidence_boundary: str
    next_actions: list[str]


def gh_json(args: list[str]) -> Any:
    cmd = ["gh", *args]
    try:
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("GitHub CLI 'gh' was not found on PATH.") from exc
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "GitHub CLI command failed")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"GitHub CLI returned non-JSON output: {proc.stdout[:400]}") from exc


def pr_payload(repo: str, pr: int) -> dict[str, Any]:
    fields = [
        "number",
        "title",
        "url",
        "isDraft",
        "headRefName",
        "baseRefName",
        "body",
        "files",
        "commits",
        "reviews",
        "statusCheckRollup",
    ]
    return gh_json(["pr", "view", str(pr), "--repo", repo, "--json", ",".join(fields)])


def open_prs(repo: str) -> list[dict[str, Any]]:
    return gh_json(["pr", "list", "--repo", repo, "--state", "open", "--limit", "100", "--json", "number,title,url,headRefName,baseRefName,isDraft"])


def file_names(payload: dict[str, Any]) -> list[str]:
    return [str(item.get("path", "")) for item in payload.get("files", []) if item.get("path")]


def text_for_scan(payload: dict[str, Any]) -> str:
    chunks = [str(payload.get("title", "")), str(payload.get("body", ""))]
    for review in payload.get("reviews", []) or []:
        chunks.append(str(review.get("body", "")))
    for commit in payload.get("commits", []) or []:
        chunks.append(str(commit.get("message", "")))
    return "\n".join(chunks).lower()


def status_mentions(payload: dict[str, Any]) -> list[str]:
    text = text_for_scan(payload).upper()
    found = {status for status in ALLOWED_STATUS if re.search(rf"\\b{re.escape(status)}\\b", text)}
    return sorted(found)


def build_report(repo: str, payload: dict[str, Any]) -> MirrorReport:
    files = file_names(payload)
    scan = text_for_scan(payload)
    flags: list[str] = []

    if any(term in scan for term in RISK_TERMS):
        flags.append("research-claim-language-present")
    if any(path.startswith("data/") for path in files):
        flags.append("canonical-data-change")
    if any(path.startswith("schemas/") for path in files):
        flags.append("schema-change")
    if any(path.startswith(".github/workflows/") for path in files):
        flags.append("ci-workflow-change")
    if any(path.startswith("prompts/") for path in files):
        flags.append("agent-prompt-change")

    gates = [
        Gate("PR-readable", "PASS", "Pull request metadata and changed files were read from GitHub."),
        Gate("scientific-status-separation", "CHECK", "UPI status words are scanned; workflow/check state must remain separate."),
        Gate("provenance", "CHECK", "Review source hashes, code revision and exact inputs before accepting any result."),
        Gate("mirror-forward", "CHECK", "Verify proposed forward calculation/model path."),
        Gate("mirror-inverse", "CHECK", "Verify inverse/recovery path and numerical error."),
        Gate("dimensions", "CHECK", "Check units and semantic quantity types for every bridge."),
        Gate("null-or-alternative", "CHECK", "Require a null model or explicit competing explanation where the claim is comparative."),
        Gate("independent-evidence", "CHECK", "A PR's own tests do not count as independent scientific replication."),
        Gate("promotion", "BLOCKED", "This helper never approves, merges, or promotes scientific status."),
    ]

    evidence_boundary = (
        "Software/CI results can establish exact tested behavior. They do not by themselves establish "
        "experimental evidence, physical causality, or a solved research problem."
    )

    next_actions = [
        "Inspect the diff and bind every claim to exact files, inputs, sources and commit hashes.",
        "Run forward/inverse and dimensional checks on the proposed relation.",
        "Add or verify independent evidence, held-out data, or a declared null model before stronger claims.",
        "Keep unresolved claims OPEN/STOP/HYP; do not infer EST from CI success.",
    ]

    return MirrorReport(
        repository=repo,
        pr=int(payload["number"]),
        title=str(payload.get("title", "")),
        url=str(payload.get("url", "")),
        head=str(payload.get("headRefName", "")),
        base=str(payload.get("baseRefName", "")),
        draft=bool(payload.get("isDraft", False)),
        gates=gates,
        changed_files=files,
        risk_flags=sorted(flags),
        status_mentions=status_mentions(payload),
        evidence_boundary=evidence_boundary,
        next_actions=next_actions,
    )


def print_report(report: MirrorReport) -> None:
    print(f"UPI Mirror Loop Audit: PR #{report.pr} — {report.title}")
    print(f"{report.url}")
    print(f"{report.head} -> {report.base} | draft={report.draft}")
    print("\nGATES")
    for gate in report.gates:
        print(f"[{gate.state:7}] {gate.name}: {gate.detail}")
    print("\nCHANGED FILES")
    for path in report.changed_files:
        print(f"- {path}")
    print("\nRISK FLAGS")
    for flag in report.risk_flags or ["none"]:
        print(f"- {flag}")
    print(f"\nSTATUS MENTIONS: {', '.join(report.status_mentions) or 'none'}")
    print(f"\nEVIDENCE BOUNDARY: {report.evidence_boundary}")
    print("\nNEXT ACTIONS")
    for action in report.next_actions:
        print(f"- {action}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="owner/name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pr", type=int)
    group.add_argument("--all-open", action="store_true")
    parser.add_argument("--json", dest="json_path", help="write JSON report")
    args = parser.parse_args()

    try:
        payloads = [pr_payload(args.repo, args.pr)] if args.pr else [pr_payload(args.repo, item["number"]) for item in open_prs(args.repo)]
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    reports = [build_report(args.repo, payload) for payload in payloads]
    if args.json_path:
        Path(args.json_path).write_text(
            json.dumps([asdict(report) for report in reports], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    else:
        for index, report in enumerate(reports):
            if index:
                print("\n" + "=" * 72 + "\n")
            print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

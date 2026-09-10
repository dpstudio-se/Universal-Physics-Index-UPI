"""Build a complete tagged TF catalogue and replayable six-loop workload offline."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .knot_io import dumps
from .legal_catalog import read_statute
from .legal_flow import (
    SNAPSHOT_DATE,
    DocumentFacts,
    LegalFlow,
    classify_document,
    review_routes,
    stop,
)
from .legal_tags import provision_tags

HISTORY_URL = ("https://www.riksdagen.se/sv/dokument-och-lagar/dokument/"
               "statens-offentliga-utredningar/yttrandefrihetsgrundlagen-och-internet-del-3_gpb328d3/html/")
ROOT_URL = "https://libris.kb.se/bib/18397754"
STATUTES = {"tf": ("TF", "1949-105"), "rf": ("RF", "1974-152"),
            "jo": ("JO", "2023-499"), "osl": ("OSL", "2009-400")}
CHAPTER_FAMILIES = {
    1: "Publicering, avgränsning och efterhandsansvar",
    2: "Handlingsoffentlighet och dess gränser",
    3: "Anonymitet och ansvarsfördelning",
    4: "Tryckning och tryckaransvar",
    5: "Utgivning och utgivaransvar",
    6: "Spridning och spridaransvar",
    7: "Brottskatalog och efterhandsansvar",
    8: "Ansvarskedja",
    9: "Tillsyn och åtal",
    10: "Tvångsmedel och processgränser",
    11: "Ersättningsansvar",
    12: "Särskild rättegångsordning",
    13: "Gränsöverskridande publicering",
    14: "Rättsmedel och kompletterande regler",
}


def root_trace(record: dict[str, Any]) -> dict[str, Any]:
    """Every port gets a trace, including an exact first missing historical link."""
    basis = re.findall(r"Lag \((\d{4}:\d+)\)", record["text"])
    current = {"node": record["id"], "version": "SFS " + (basis[-1] if basis else "2022:1524"),
               "status": "EST", "source": record["source_url"]}
    previous = {"node": record["id"] + " prior wording", "status": "STOP",
                "stop_reason": "No verified paragraph correspondence to the preceding wording",
                "next_observation": f"Compare {record['id']} with the prior wording and amendment concordance"}
    digital = record["id"] in {"TF 1:5", "TF 1:6", "TF 1:13", "TF 2:6", "TF 2:7",
                               "TF 7:27", "TF 7:28", "TF 9:9", "TF 9:10"}
    inherited_principle = record["id"] in {"TF 1:1", "TF 1:9", "TF 2:1", "TF 7:1", "TF 12:1"}
    return {"status": "STOP", "stop_reason": previous["stop_reason"],
            "next_observation": previous["next_observation"], "path": [current, previous],
            "root": {"id": "TF1766-HISTORICAL", "source": ROOT_URL, "status": "EST",
                     "scope": "existence and identity of the historical publication"},
            "family": CHAPTER_FAMILIES[record["chapter"]],
            "candidate_tags": ["ADDED", "MODIFIED"] if digital else ["INHERITED", "MODIFIED", "ADDED"],
            "candidate_status": "HYP", "confirmed_tag": None,
            "principle_link": {"status": "DER", "tag": "INHERITED", "source": HISTORY_URL,
                               "scope": "functional principle only; not exact wording or uninterrupted validity"}
            if inherited_principle else None,
            "principle_history_source": HISTORY_URL,
            "unverified_milestones": ["1949/1950", "1812", "1810", "1774", "1766"],
            "scope": "Principle ancestry is not paragraph identity or uninterrupted validity"}


def lifecycle(text: str) -> dict[str, Any]:
    if "Har upphävts genom lag" in text:
        return {"active": False, "tag": "REPEALED", "status": "EST"}
    if "Har betecknats" in text:
        return {"active": False, "tag": "MODIFIED", "status": "EST", "kind": "renumbered"}
    future = re.search(r"Träder i kraft I:(\d{4}-\d{2}-\d{2})", text)
    expires = re.search(r"Upphör att gälla U:(\d{4}-\d{2}-\d{2})", text)
    if future and future[1] > SNAPSHOT_DATE or expires and expires[1] <= SNAPSHOT_DATE:
        return {"active": False, "tag": "MODIFIED", "status": "EST", "kind": "outside_snapshot_date"}
    if "Träder i kraft I:den dag" in text or "Upphör att gälla U:den dag" in text:
        return {"active": None, **stop("Commencement date not established", "Find the commencement decision")}
    return {"active": True, "tag": None, "status": "DER", "scope": "consolidated snapshot date only"}


def make_catalog(source_dir: Path) -> dict[str, Any]:
    tags = provision_tags()
    sources = []
    for name, (statute, sfs) in STATUTES.items():
        sources.append(read_statute(source_dir / f"{name}.html", statute=statute,
                                    url=f"https://data.riksdagen.se/dokument/sfs-{sfs}.html",
                                    retrieved_on=SNAPSHOT_DATE))
    tf = sources[0]
    ids = [r["id"] for r in tf["records"]]
    if set(ids) != set(tags) or len(ids) != len(tags):
        raise ValueError("source inventory changed: review each paragraph before rebuilding tags")
    for record in tf["records"]:
        record["tags"] = tags[record["id"]]
        record["tag_status"] = "DER"
        record["tag_scope"] = "functional reading aid; apply full text and referenced law"
        record["lifecycle"] = lifecycle(record["text"])
        record["root_trace"] = root_trace(record)
    supporting: list[dict[str, Any]] = []
    for source in sources[1:]:
        selected = [r for r in source["records"] if
                    source["statute"] == "JO" and 11 <= int(r["section"]) <= 23 or
                    source["statute"] == "OSL" and r["chapter"] == 6 or
                    source["statute"] == "RF" and r["id"] in
                    {"RF 11:14", "RF 12:10", "RF 13:1", "RF 13:2", "RF 13:3", "RF 13:6"}]
        supporting.extend({**r, "lifecycle": lifecycle(r["text"])} for r in selected)
    return {"format": "upi-oden-legal-workload", "version": "1.0", "snapshot_date": SNAPSHOT_DATE,
            "status": "DER", "verification_type": "software_test",
            "claims_experimental_verification": False,
            "sources": [{k: v for k, v in source.items() if k != "records"} for source in sources],
            "scope": "all TF chapter 1–14 paragraph anchors; transition provisions require separate review",
            "provisions": tf["records"], "supporting_provisions": supporting,
            "coverage": {"total": len(ids), "active": sum(r["lifecycle"]["active"] is True
                                                            for r in tf["records"]),
                         "by_chapter": dict(sorted(Counter(r["chapter"] for r in tf["records"]).items()))},
            "loops": [
                {"id": "A", "name": "ROOT-TRACE", "operation": "root_trace", "scope": "historical correspondence"},
                {"id": "B", "name": "FORWARD-FLOW", "operation": "LegalFlow.apply", "scope": "latest-state ledger"},
                {"id": "C", "name": "BOUNDARY", "operation": "publication_boundary", "scope": "conditional TF applicability"},
                {"id": "D", "name": "DOCUMENT", "operation": "classify_document", "scope": "assessed document facts"},
                {"id": "E", "name": "ERROR/REVIEW", "operation": "review_routes", "scope": "parallel remedy and oversight"},
                {"id": "F", "name": "CLOSED-FEEDBACK", "operation": "LegalFlow.feedback/verify_correction",
                 "scope": "record review then verify observed implementation"}],
            "historical_boundary": {"status": "STOP", "stop_reason": "Full version concordance to 1766 is not established",
                                    "next_observation": "Obtain previous wordings and article-level concordances",
                                    "source": HISTORY_URL,
                                    "finding": "1766 had exceptions; 1774 and later reforms break any simple unchanged-lineage claim"}}


def demo_results() -> dict[str, Any]:
    facts = DocumentFacts(authority=True, document=True, stored=True, received=True, drawn_up=False,
                          exception="none", secrecy="partial", secrecy_basis="synthetic OSL assessment",
                          provenance=("synthetic fixture; no real person's data",))
    flow = LegalFlow("synthetic-feedback", {"disclosure": "refused"})
    flow.apply("TF 2:19", {"value": "appeal pending", "provenance": ["synthetic refusal"]}, expected=flow.token)
    flow.feedback("JO", "synthetic JO statement", "criticism", expected=flow.token)
    flow.verify_correction("synthetic JO statement", "synthetic implementation check",
                           "disclosed", "still refused", expected=flow.token)
    return {"verification_type": "software_test", "document": classify_document(facts),
            "minister_routes": review_routes("minister", issue="disclosure"),
            "authority_routes": review_routes("authority", issue="disclosure"),
            "feedback": flow.chain.to_dict()}


def render_markdown(catalog: dict[str, Any]) -> str:
    lines = ["# TF – paragrafkarta och sex kontroll-loopar", "",
             f"Källversion: SFS 2022:1524. Kontrolldatum: {catalog['snapshot_date']}.",
             "", "EST = återgiven källtext; DER = funktionstaggning; HYP = historisk kandidat.",
             "Alla ROOT-TRACE har en uttrycklig STOP vid första obelagda versionslänk.",
             "Tabellordning är lagens textordning, inte en universell exekveringsordning.", "",
             "| Lagrum | Funktion/rubrik | Taggar (DER) | Livscykel | Historisk kontroll |",
             "|---|---|---|---|---|"]
    for r in catalog["provisions"]:
        state = "Gällande i snapshot" if r["lifecycle"]["active"] else r["lifecycle"]["tag"]
        lines.append(f"| [{r['id']}]({r['source_url']}) | {r['heading']} | {' / '.join(r['tags'])} | {state} | STOP: föregående lydelse → 1766 ej belagd |")
    lines += ["", "Full källtext, hashvärden, möjliga historiktaggar och nästa observation finns i JSON-katalogen."]
    return "\n".join(lines) + "\n"


def render_html(catalog: dict[str, Any]) -> str:
    rows = []
    for r in catalog["provisions"]:
        e = html.escape
        if not re.fullmatch(r"https://data\.riksdagen\.se/dokument/sfs-1949-105\.html#K\d+P\d+[a-z]?",
                            r["source_url"]):
            raise ValueError("unexpected TF source URL")
        rows.append(f"<details><summary>{e(r['id'])} · {e(r['heading'])}</summary>"
                    f"<p><b>DER:</b> {e(' · '.join(r['tags']))}</p>"
                      f"<p>Livscykel: {e('Gällande i källversionen' if r['lifecycle']['active'] else str(r['lifecycle']['tag']))}</p>"
                    f"<blockquote>{e(r['text'])}</blockquote><p><a href='{e(r['source_url'], quote=True)}'>Källtext</a></p>"
                    f"<p><b>ROOT-TRACE / STOP:</b> {e(r['root_trace']['stop_reason'])}</p>"
                    f"<p>Nästa observation: {e(r['root_trace']['next_observation'])}</p></details>")
    return ("<!doctype html><html lang='sv'><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
            "<title>ODEN · TF kontroll-loopar</title><link rel='icon' href='data:,'><style>body{font:16px/1.6 system-ui;max-width:1000px;margin:auto;padding:24px;background:#101820;color:#e4eeee}a{color:#91e6c6}details{border-top:1px solid #49606b;padding:12px 0}summary{cursor:pointer}blockquote{margin:12px 0;padding:12px;border-left:3px solid #91e6c6;white-space:pre-wrap;overflow-wrap:anywhere}p{overflow-wrap:anywhere}</style>"
            "<h1>ODEN · TF:s sex kontroll-loopar</h1><p>189 gällande paragrafer + 4 historiska markörer. SFS 2022:1524 · kontrollerad 2026-09-10.</p>"
            "<p>Funktionstaggar är läshjälp. Historiska länkar kräver belägg. Ingen automatisk rättstillämpning.</p>"
            "<p><a href='tf-workload.json'>Fullständig JSON</a> · <a href='tf-loops.json'>Körda kontrollfall</a></p>"
            + "".join(rows) + "</html>")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, help="directory of downloaded official tf/rf/jo/osl.html")
    parser.add_argument("--catalog", type=Path, default=Path("examples/legal/tf-workload.json"))
    parser.add_argument("--output", type=Path, default=Path("dist/tf"))
    args = parser.parse_args()
    catalog = make_catalog(args.sources) if args.sources else json.loads(args.catalog.read_text(encoding="utf-8"))
    if catalog.get("format") != "upi-oden-legal-workload" or catalog.get("snapshot_date") != SNAPSHOT_DATE:
        raise ValueError("catalogue format/date must match the reviewed workload")
    if {r["id"] for r in catalog["provisions"]} != set(provision_tags()):
        raise ValueError("catalogue inventory differs from reviewed tags")
    for record in catalog["provisions"]:
        if hashlib.sha256(record["text"].encode()).hexdigest() != record["text_sha256"]:
            raise ValueError("catalogue source text hash mismatch")
    args.output.mkdir(parents=True, exist_ok=True)
    files = {"tf-workload.json": dumps(catalog), "tf-loops.json": dumps(demo_results()),
             "tf-paragraph-map.md": render_markdown(catalog), "index.html": render_html(catalog)}
    for name, data in files.items():
        (args.output / name).write_text(data, encoding="utf-8")
    manifest = {name: hashlib.sha256(data.encode()).hexdigest() for name, data in files.items()}
    (args.output / "manifest.json").write_text(dumps(manifest), encoding="utf-8")
    print(dumps(catalog["coverage"]).strip())


if __name__ == "__main__":
    main()

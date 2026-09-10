"""Offline, source-preserving catalogue of statute provisions, not a legal decision maker."""

from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


class StatuteParser(HTMLParser):
    """Read explicit Riksdagen paragraph anchors; headings never become statute text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.records: list[dict[str, Any]] = []
        self.current: dict[str, Any] | None = None
        self.parts: list[str] = []
        self.heading: list[str] | None = None
        self.title = ""
        self.chapter_title = ""
        self.stopped = False
        self.pending_heading: int | None = None

    def flush(self) -> None:
        if self.current is not None:
            parts = self.parts[:self.pending_heading] if self.pending_heading is not None else self.parts
            value = re.sub(r"\s+", " ", "".join(parts)).strip()
            self.records.append({**self.current, "text": value,
                                 "text_sha256": hashlib.sha256(value.encode()).hexdigest()})
        self.current = None
        self.parts = []
        self.pending_heading = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        anchor = attributes.get("name") or ""
        if anchor == "overgang":
            self.flush()
            self.stopped = True
        if tag in {"h3", "h4"}:
            if self.pending_heading is None:
                self.pending_heading = len(self.parts)
            self.heading = []
        if tag == "a" and attributes.get("class") == "paragraf" and not self.stopped:
            self.flush()
            match = re.fullmatch(r"(?:K(\d+))?P(\d+[a-z]?)", anchor)
            if match is None:
                raise ValueError(f"unknown paragraph anchor: {anchor}")
            self.current = {"chapter": int(match[1] or 0), "section": match[2],
                            "anchor": anchor, "heading": self.title,
                            "chapter_title": self.chapter_title}
        if tag in {"br", "p"} and self.current is not None:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h3", "h4"} and self.heading is not None:
            self.title = re.sub(r"\s+", " ", "".join(self.heading)).strip()
            if self.current is not None:
                self.parts.append(" " + self.title + " ")
            if tag == "h3":
                self.chapter_title = self.title
            self.heading = None

    def handle_data(self, data: str) -> None:
        if self.heading is not None:
            self.heading.append(data)
        elif self.current is not None:
            if data.strip():
                self.pending_heading = None
            self.parts.append(data)


def read_statute(path: Path, *, statute: str, url: str, retrieved_on: str) -> dict[str, Any]:
    raw = path.read_bytes()
    parser = StatuteParser()
    parser.feed(raw.decode("utf-8-sig"))
    parser.flush()
    if not parser.records:
        raise ValueError("source has no explicit statute paragraph anchors")
    amendments = re.findall(r"t\.o\.m\. SFS ([\d:]+)", raw.decode("utf-8-sig"))
    return {"statute": statute, "source_url": url, "retrieved_on": retrieved_on,
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "amended_through": amendments[0] if amendments else None,
            "extraction": "explicit paragraph anchors; whitespace collapsed; headings separate",
            "records": [{**r, "id": f"{statute} {r['chapter']}:{r['section']}"
                         if r["chapter"] else f"{statute} {r['section']}",
                         "source_url": url + "#" + r["anchor"], "status": "EST"}
                        for r in parser.records]}

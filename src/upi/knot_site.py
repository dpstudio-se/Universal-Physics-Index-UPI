"""Build an allowlisted ODEN static bundle or analyze a local path document."""

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from .knot_examples import example_document, example_report
from .knot_io import analyze_document, dumps


def build(output: Path, report: dict | None = None) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    static = Path(__file__).parent / "contribute" / "static"
    files = {"index.html": (static / "oden.html").read_bytes(),
             "oden.css": (static / "oden.css").read_bytes(),
             "oden.js": (static / "oden.js").read_bytes(),
             "knots.json": dumps(report if report is not None else example_report()).encode("utf-8"),
             "paths.example.json": dumps(example_document()).encode("utf-8")}
    manifest = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    files["manifest.json"] = dumps(manifest).encode("utf-8")
    for name, data in files.items():
        (output / name).write_bytes(data)
    archive = output.parent / "oden-knot-engine.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
        for name, data in files.items():
            bundle.writestr("oden/" + name, data)
    return archive


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="upi-oden-paths JSON to analyze")
    parser.add_argument("--output", type=Path, default=Path("dist/oden"))
    args = parser.parse_args()
    report = analyze_document(json.loads(args.input.read_text(encoding="utf-8"))) if args.input else None
    print(build(args.output, report))


if __name__ == "__main__":
    main()

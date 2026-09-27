# UPI PDF Inspector (Rust)

A deterministic PDF inspection adapter for the Universal Physics Index (UPI).

Pipeline: PDF -> inspect -> extract text -> classify evidence -> UPI JSON

Evidence labels mirror UPI status concepts: EST, DER, HYP, SYM, ERR, STOP and Unknown.
This crate does not decide whether a physics claim is scientifically true. It preserves page-level provenance and emits machine-readable material for UPI review.

CLI: cargo run --release -- path/to/document.pdf

The command prints JSON and writes document.pdf.upi.json. OCR, table recognition, coordinate extraction, and scientific verification remain separate layers so extraction does not silently become scientific validation.

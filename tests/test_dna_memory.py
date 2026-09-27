from upi.dna_memory import DNAReader, DNAWriter


def test_dna_memory_roundtrip(tmp_path):
    w = DNAWriter(tmp_path / ".dna_minne")
    event = w.write({"key": "test", "value": 7.834125}, status="TEST")
    assert DNAReader(tmp_path / ".dna_minne").latest() == event


def test_dna_memory_detects_tamper(tmp_path):
    root = tmp_path / ".dna_minne"
    DNAWriter(root).write({"key": "test"}, status="TEST")
    p = root / "memory.jsonl"
    text = p.read_text(encoding="utf-8").replace('"test"', '"tampered"', 1)
    p.write_text(text, encoding="utf-8")
    try:
        DNAReader(root).read()
    except ValueError as exc:
        assert "integrity" in str(exc)
    else:
        raise AssertionError("tampering was not detected")

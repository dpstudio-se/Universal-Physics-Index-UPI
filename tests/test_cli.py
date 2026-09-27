import json
import sys
from pathlib import Path

import pytest

from upi.cli import main


def test_frequency_to_mass_explains_boundary(
    capsys: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "argv", ["upi", "frequency-to-mass", "8"])
    assert main() is None
    payload = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert "not the mass" in payload["interpretation"]


def test_invalid_file_has_nonzero_exit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "invalid.json"
    path.write_text('{"status":"HYP"}', encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["upi", "validate", str(path)])
    with pytest.raises(SystemExit) as raised:
        main()
    assert raised.value.code == 1


def test_address_command_uses_current_address_model(
    capsys: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "upi",
            "address",
            "--domain",
            "TEST",
            "--generation",
            "1",
            "--torus",
            "LAB",
            "--node",
            "N1",
        ],
    )
    assert main() is None
    assert json.loads(capsys.readouterr().out)["address_string"] == "UPI<TEST,1,LAB,N1>"  # type: ignore[attr-defined]


def test_self_test_runs_inside_out(
    tmp_path: Path, capsys: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    calls = []

    class Result:
        returncode = 0

    def fake_run(command: list[str], **kwargs: object) -> Result:
        calls.append(command)
        return Result()

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr(sys, "argv", ["upi", "self-test", str(tmp_path)])
    assert main() is None

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PASS"
    assert payload["direction"] == "inside-out"
    assert calls[0][1:] == ["tools/upi_system_audit.py"]
    assert calls[1][1:3] == ["-m", "pytest"]
    assert calls[2][1:3] == ["-m", "ruff"]
    assert calls[3][1:3] == ["-m", "mypy"]

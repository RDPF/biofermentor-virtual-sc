from pathlib import Path

from biofermentor.validation_report import (
    generate_validation_payload,
    parameter_sha256,
    render_markdown,
    write_outputs,
    check_outputs,
)
from biofermentor.core import defaults


def test_validation_payload_is_deterministic():
    a = generate_validation_payload()
    b = generate_validation_payload()
    assert a == b
    assert a["default_parameter_sha256"] == parameter_sha256(defaults())
    assert all(case["oxygen_status"] == "PASS" for case in a["reference_cases"])


def test_validation_report_round_trip(tmp_path):
    payload = write_outputs(tmp_path, include_runtime=False)
    assert (tmp_path / "VALIDATION_REPORT.md").exists()
    assert (tmp_path / "validation_results.json").exists()
    assert check_outputs(tmp_path)
    text = (tmp_path / "VALIDATION_REPORT.md").read_text(encoding="utf-8")
    assert payload["version"] in text
    assert "O₂ error" in text


def test_validation_check_fails_after_manual_tamper(tmp_path):
    write_outputs(tmp_path)
    p = tmp_path / "VALIDATION_REPORT.md"
    p.write_text(p.read_text(encoding="utf-8") + "\nmanual edit\n", encoding="utf-8")
    assert not check_outputs(tmp_path)

"""Reproducible scientific validation-report generator for v3.0."""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np

from biofermentor import __version__
from biofermentor.core import defaults, BiofermentorSimulator, SCProcess
from biofermentor.core.validation import physiological_self_tests, numerical_self_tests


REFERENCE_CASES = (12.0, 30.0, 48.0)
REFERENCE_DT = 0.0025


def canonical_parameter_json(p=None):
    if p is None:
        p = defaults()
    return json.dumps(p, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def parameter_sha256(p=None):
    return hashlib.sha256(canonical_parameter_json(p).encode("utf-8")).hexdigest()


def generate_validation_payload():
    """Generate deterministic reference-validation data.

    No timestamp, OS, Python version or git commit is included here so that
    version-controlled outputs can be regenerated and compared byte-for-byte.
    """
    p0 = defaults()
    physiology = physiological_self_tests(SCProcess(p0), p0)
    numerical = numerical_self_tests(BiofermentorSimulator, defaults)

    cases = []
    for tf in REFERENCE_CASES:
        p = defaults()
        p["mode"] = "Fed-batch"
        p["feed_strategy"] = "Exponencial"
        p["tf"] = tf
        p["dt"] = REFERENCE_DT
        r = BiofermentorSimulator(p).run()
        cases.append({
            "tf_h": tf,
            "dt_h": REFERENCE_DT,
            "carbon_error_pct": r["dynamic_carbon_audit"]["error_pct"],
            "carbon_recovery_pct": r["dynamic_carbon_audit"]["recovery_pct"],
            "carbon_status": r["dynamic_carbon_audit"]["status"],
            "nitrogen_error_pct": r["dynamic_nitrogen_audit"]["error_pct"],
            "nitrogen_recovery_pct": r["dynamic_nitrogen_audit"]["recovery_pct"],
            "nitrogen_status": r["dynamic_nitrogen_audit"]["status"],
            "oxygen_error_pct": r["dynamic_oxygen_audit"]["error_pct"],
            "oxygen_recovery_pct": r["dynamic_oxygen_audit"]["recovery_pct"],
            "oxygen_status": r["dynamic_oxygen_audit"]["status"],
            "overall_status": r["integrity_report"]["overall_status"],
        })

    return {
        "software": "Biofermentor Virtual SC",
        "version": __version__,
        "validation_schema": "2.4",
        "default_parameter_sha256": parameter_sha256(p0),
        "reference_dt_h": REFERENCE_DT,
        "reference_cases": cases,
        "physiological_self_tests": physiology,
        "numerical_self_tests": numerical,
        "scientific_scope": (
            "Model-integrity validation only; this does not constitute "
            "experimental biological validation."
        ),
    }


def runtime_metadata():
    """Return volatile execution metadata, intentionally kept out of stable report."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        commit = None
    return {
        "generated_at_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "git_commit": commit,
    }


def render_markdown(payload):
    lines = [
        "# Validation Report — v" + payload["version"],
        "",
        "**Automatically generated. Do not edit numerical results manually.**",
        "",
        "## Reproducibility identity",
        "",
        f"- Software version: `{payload['version']}`",
        f"- Default-parameter SHA-256: `{payload['default_parameter_sha256']}`",
        f"- Reference integration step: `{payload['reference_dt_h']}` h",
        "",
        "Volatile runtime metadata is stored separately in `validation_runtime.json`",
        "when the generator is executed with `--runtime`.",
        "",
        "## Reference dynamic mass balances",
        "",
        "| Final time | Carbon error | C | Nitrogen error | N | O₂ error | O₂ | Overall |",
        "|---:|---:|---|---:|---|---:|---|---|",
    ]
    for c in payload["reference_cases"]:
        lines.append(
            f"| {c['tf_h']:.0f} h "
            f"| {c['carbon_error_pct']:+.3f}% | {c['carbon_status']} "
            f"| {c['nitrogen_error_pct']:+.3f}% | {c['nitrogen_status']} "
            f"| {c['oxygen_error_pct']:+.5f}% | {c['oxygen_status']} "
            f"| {c['overall_status']} |"
        )

    lines += [
        "",
        "Default elemental-balance classification:",
        "",
        "- PASS: absolute error ≤ 5%",
        "- WARNING: 5% < absolute error < 10%",
        "- FAIL: absolute error ≥ 10%",
        "",
        "## Physiological semantic self-tests",
        "",
    ]
    for name, ok in payload["physiological_self_tests"].items():
        lines.append(f"- `{name}`: **{'PASS' if ok else 'FAIL'}**")

    lines += ["", "## Numerical self-tests", ""]
    for case, checks in payload["numerical_self_tests"].items():
        lines.append(f"### {case}")
        lines.append("")
        for name, ok in checks.items():
            lines.append(f"- `{name}`: **{'PASS' if ok else 'FAIL'}**")
        lines.append("")

    lines += [
        "## Interpretation",
        "",
        "The carbon and nitrogen audits quantify closure of modeled elemental inventories.",
        "The oxygen audit is a numerical identity check of the liquid-phase O₂ balance:",
        "",
        r"\[",
        r"\frac{d(C_LV)}{dt}=V(OTR-OUR).",
        r"\]",
        "",
        "It therefore checks consistency among `CL`, `V`, `kLa`, `C*` and `OUR`; it",
        "does **not** independently validate the empirical `kLa` correlation or biological OUR.",
        "",
        payload["scientific_scope"],
        "",
        "Experimental validation against independent fermentation data remains the next",
        "major scientific maturity milestone.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(output_dir, include_runtime=False):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = generate_validation_payload()

    md = render_markdown(payload)
    json_text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

    (output_dir / "VALIDATION_REPORT.md").write_text(md, encoding="utf-8")
    (output_dir / "validation_results.json").write_text(json_text, encoding="utf-8")

    if include_runtime:
        runtime_text = json.dumps(
            runtime_metadata(), indent=2, ensure_ascii=False, sort_keys=True
        ) + "\n"
        (output_dir / "validation_runtime.json").write_text(runtime_text, encoding="utf-8")

    return payload


def check_outputs(output_dir):
    """Return True only if stable generated outputs match version-controlled files."""
    output_dir = Path(output_dir)
    payload = generate_validation_payload()
    expected_md = render_markdown(payload)
    expected_json = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

    md_path = output_dir / "VALIDATION_REPORT.md"
    js_path = output_dir / "validation_results.json"
    if not md_path.exists() or not js_path.exists():
        return False
    return (
        md_path.read_text(encoding="utf-8") == expected_md
        and js_path.read_text(encoding="utf-8") == expected_json
    )


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default=".")
    ap.add_argument("--runtime", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    if args.check:
        ok = check_outputs(args.output_dir)
        print("VALIDATION_REPORT_SYNC=PASS" if ok else "VALIDATION_REPORT_SYNC=FAIL")
        return 0 if ok else 1

    payload = write_outputs(args.output_dir, include_runtime=args.runtime)
    print(
        f"Generated validation report for v{payload['version']} "
        f"in {Path(args.output_dir).resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

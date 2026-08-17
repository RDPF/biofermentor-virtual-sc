"""CLI/report generator for v3.0 frozen-parameter independent validation."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from biofermentor import __version__
from biofermentor.independent_validation import run_independent_validation
from biofermentor.validation_data import load_dataset_directory


def render_markdown(report):
    def f(v):
        return "NA" if v is None else f"{float(v):.6g}"
    lines = [
        "# Independent Validation Report",
        "",
        f"- Software version: `{__version__}`",
        f"- Analysis: `{report['analysis_type']}`",
        f"- No parameter fitting performed: `{report['no_parameter_fitting_performed']}`",
        f"- Dataset: `{report['dataset_id']}`",
        f"- Dataset role: `{report['dataset_role']}`",
        f"- Data origin: `{report['data_origin']}`",
        f"- Data SHA-256: `{report['data_sha256']}`",
        f"- Metadata SHA-256: `{report['metadata_sha256']}`",
        f"- Calibration lock SHA-256: `{report['calibration_lock_sha256']}`",
        f"- Calibration dataset: `{report['calibration_dataset_id']}`",
        f"- Optimized parameter SHA-256 from lock: `{report['optimized_parameter_sha256_from_lock']}`",
        f"- Prediction parameter SHA-256: `{report['prediction_parameter_sha256']}`",
        f"- Scientific qualification: **{report['qualification']['status']}**",
        f"- Software integrity: **{report['software_integrity']['overall_status']}**",
        f"- Aggregate mean NRMSE(range): `{report['aggregate_mean_NRMSE_range']}`",
        "",
        "## Frozen parameters",
        "",
        "| Parameter | Value |",
        "|---|---:|",
    ]
    for k, v in report["frozen_optimized_values"].items():
        lines.append(f"| `{k}` | {float(v):.8g} |")
    lines += [
        "",
        "## Metrics by observable",
        "",
        "| Variable | n | RMSE | MAE | NRMSE(range) | R² | MBE | Endpoint error |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for var, c in report["comparisons"].items():
        m = c["metrics"]
        lines.append(
            f"| {var} | {m['n']} | {f(m['RMSE'])} | {f(m['MAE'])} | "
            f"{f(m['NRMSE_range'])} | {f(m['R2'])} | {f(m['MBE'])} | {f(c['endpoint_error'])} |"
        )
    lines += [
        "",
        "## Elemental integrity during prediction",
        "",
        f"- Carbon: **{report['dynamic_carbon']['status']}**, error `{report['dynamic_carbon']['error_pct']:.6g}%`",
        f"- Nitrogen: **{report['dynamic_nitrogen']['status']}**, error `{report['dynamic_nitrogen']['error_pct']:.6g}%`",
        f"- Oxygen: **{report['dynamic_oxygen']['status']}**, error `{report['dynamic_oxygen']['error_pct']:.6g}%`",
        "",
        "## Qualification reasons",
        "",
    ]
    if report["qualification"].get("reasons"):
        for r in report["qualification"]["reasons"]:
            lines.append(f"- {r}")
    else:
        lines.append("- None")
    lines += [
        "",
        "## Interpretation",
        "",
        report["scientific_interpretation"],
        "",
        "## Scientific limitations",
        "",
    ]
    for item in report["scientific_limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(report, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out/"independent_validation_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)+"\n", encoding="utf-8")
    (out/"independent_validation_report.md").write_text(render_markdown(report), encoding="utf-8")
    with (out/"independent_validation_predictions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dataset_id","observable","index","observed","predicted","residual_model_minus_observed"])
        for obs, comp in report["comparisons"].items():
            for i, (o,p,r) in enumerate(zip(comp["observed"], comp["predicted"], comp["residuals_model_minus_observed"])):
                w.writerow([report["dataset_id"], obs, i, o, p, r])
    files = ["independent_validation_report.json","independent_validation_report.md","independent_validation_predictions.csv"]
    manifest = {
        "analysis_type": report["analysis_type"],
        "dataset_id": report["dataset_id"],
        "no_parameter_fitting_performed": True,
        "qualification": report["qualification"],
        "inputs": {
            "data_sha256": report["data_sha256"],
            "metadata_sha256": report["metadata_sha256"],
            "calibration_lock_sha256": report["calibration_lock_sha256"],
            "optimized_parameter_sha256_from_lock": report["optimized_parameter_sha256_from_lock"],
        },
        "outputs": {},
    }
    for name in files:
        manifest["outputs"][name] = hashlib.sha256((out/name).read_bytes()).hexdigest()
    (out/"independent_validation_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True)+"\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_dir")
    ap.add_argument("--calibration-lock", required=True)
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--allow-calibration-prediction", action="store_true")
    args = ap.parse_args(argv)
    ds = load_dataset_directory(args.dataset_dir)
    report, _ = run_independent_validation(
        ds, args.calibration_lock,
        allow_calibration_prediction=args.allow_calibration_prediction,
    )
    out = Path(args.output_dir) if args.output_dir else Path(args.dataset_dir)/"independent_validation_results"
    write_outputs(report, out)
    print(f"Independent-validation artifacts written to {out.resolve()}")
    print(f"No parameter fitting performed: {report['no_parameter_fitting_performed']}")
    print(f"Scientific qualification: {report['qualification']['status']}")
    print(f"Aggregate mean NRMSE(range): {report['aggregate_mean_NRMSE_range']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

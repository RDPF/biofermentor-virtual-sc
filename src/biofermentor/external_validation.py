import argparse
import json
import csv
import hashlib
from pathlib import Path

from biofermentor.validation_data import (
    load_dataset_directory,
    run_zero_fit_validation,
    qualification,
)


def render_markdown(report):
    lines = [
        f"# External Validation Baseline — {report['dataset_id']}",
        "",
        f"- Analysis: `{report['analysis_type']}`",
        f"- Dataset role: `{report['dataset_role']}`",
        f"- Data origin: `{report['data_origin']}`",
        f"- Data SHA-256: `{report['data_sha256']}`",
        f"- Metadata SHA-256: `{report['metadata_sha256']}`",
        f"- Parameter SHA-256: `{report['parameter_sha256']}`",
        f"- Software integrity: **{report['software_integrity']['overall_status']}**",
        f"- Scientific qualification: **{report['qualification']['status']}**",
        f"- Aggregate mean NRMSE(range): `{report['aggregate_mean_NRMSE_range']}`",
        "",
        "## Metrics by observable",
        "",
        "| Variable | n | RMSE | MAE | NRMSE(range) | R² | MBE |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for var, c in report["comparisons"].items():
        m = c["metrics"]
        def f(v):
            return "NA" if v is None else f"{v:.6g}"
        lines.append(
            f"| {var} | {m['n']} | {f(m['RMSE'])} | {f(m['MAE'])} | "
            f"{f(m['NRMSE_range'])} | {f(m['R2'])} | {f(m['MBE'])} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        report["scientific_interpretation"],
        "",
        "This report does not imply experimental validation unless the dataset role/origin",
        "and provenance establish that the observations are genuinely external experimental data.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_dir")
    ap.add_argument("--output-dir", default=None)
    args = ap.parse_args(argv)

    ds = load_dataset_directory(args.dataset_dir)
    report = run_zero_fit_validation(ds)
    report["qualification"] = qualification(ds, report)

    out = Path(args.output_dir) if args.output_dir else Path(args.dataset_dir) / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out/"zero_fit_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out/"zero_fit_report.md").write_text(render_markdown(report), encoding="utf-8")

    # Long-form residual/prediction table for independent inspection.
    with (out/"zero_fit_predictions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dataset_id","observable","time_h","observed","predicted","residual_model_minus_observed"])
        for observable, comp in report["comparisons"].items():
            for t, o, p, r in zip(ds.time_h, comp["observed"], comp["predicted"], comp["residuals_model_minus_observed"]):
                w.writerow([ds.dataset_id, observable, float(t), o, p, r])

    # Baseline identity manifest.
    files = ["zero_fit_report.json", "zero_fit_report.md", "zero_fit_predictions.csv"]
    manifest = {
        "analysis_type": "zero_fit_external_comparison",
        "dataset_id": ds.dataset_id,
        "qualification": report["qualification"],
        "inputs": {
            "data_sha256": report["data_sha256"],
            "metadata_sha256": report["metadata_sha256"],
            "parameter_sha256": report["parameter_sha256"],
        },
        "outputs": {},
    }
    for name in files:
        manifest["outputs"][name] = hashlib.sha256((out/name).read_bytes()).hexdigest()
    (out/"baseline_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"External-validation baseline written to {out.resolve()}")
    print(f"Scientific qualification: {report['qualification']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

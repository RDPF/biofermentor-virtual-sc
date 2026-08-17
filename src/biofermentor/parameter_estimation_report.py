"""CLI/report generator for v3.0 parameter estimation."""
from __future__ import annotations

import argparse
import csv
import json
import hashlib
from pathlib import Path

from biofermentor import __version__
from biofermentor.parameter_estimation import estimate_parameters, PRESETS
from biofermentor.validation_data import load_dataset_directory


def render_markdown(report):
    def f(x):
        return "NA" if x is None else f"{float(x):.6g}"

    lines = [
        "# Parameter Estimation Report",
        "",
        f"- Software version: `{__version__}`",
        f"- Analysis: `{report['analysis_type']}`",
        f"- Dataset: `{report['dataset_id']}`",
        f"- Dataset role: `{report['dataset_role']}`",
        f"- Data origin: `{report['data_origin']}`",
        f"- Data SHA-256: `{report['data_sha256']}`",
        f"- Metadata SHA-256: `{report['metadata_sha256']}`",
        f"- Initial parameter SHA-256: `{report['initial_parameter_sha256']}`",
        f"- Optimized parameter SHA-256: `{report['optimized_parameter_sha256']}`",
        f"- Optimizer: `{report['optimizer']['name']}`",
        f"- Success: `{report['optimizer']['success']}`",
        f"- Function evaluations: `{report['optimizer']['nfev']}`",
        f"- Final software integrity: **{report['software_integrity_after_fit']['overall_status']}**",
        "",
        "## Objective",
        "",
        f"- Initial objective: `{report['initial_objective']:.8g}`",
        f"- Final objective: `{report['final_objective']:.8g}`",
        f"- Reduction factor: `{report['objective_reduction_factor']}`",
        f"- Initial aggregate mean NRMSE(range): `{report['initial_aggregate_mean_NRMSE_range']}`",
        f"- Fitted aggregate mean NRMSE(range): `{report['fitted_aggregate_mean_NRMSE_range']}`",
        "",
        "## Estimated parameters",
        "",
        "| Parameter | Lower | Initial | Optimized | Upper |",
        "|---|---:|---:|---:|---:|",
    ]
    for p in report["fit_parameters"]:
        lo, hi = report["bounds"][p]
        lines.append(
            f"| `{p}` | {lo:.6g} | {report['initial_values'][p]:.6g} | "
            f"{report['optimized_values'][p]:.6g} | {hi:.6g} |"
        )

    lines += [
        "",
        "## Metrics after fitting",
        "",
        "| Variable | n | RMSE | MAE | NRMSE(range) | R² | MBE |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for var, m in report["fitted_metrics"].items():
        lines.append(
            f"| {var} | {m['n']} | {f(m['RMSE'])} | {f(m['MAE'])} | "
            f"{f(m['NRMSE_range'])} | {f(m['R2'])} | {f(m['MBE'])} |"
        )

    lines += [
        "",
        "## Elemental integrity after fitting",
        "",
        f"- Carbon: **{report['dynamic_carbon_after_fit']['status']}**, "
        f"error `{report['dynamic_carbon_after_fit']['error_pct']:.6g}%`",
        f"- Nitrogen: **{report['dynamic_nitrogen_after_fit']['status']}**, "
        f"error `{report['dynamic_nitrogen_after_fit']['error_pct']:.6g}%`",
        f"- Oxygen: **{report['dynamic_oxygen_after_fit']['status']}**, "
        f"error `{report['dynamic_oxygen_after_fit']['error_pct']:.6g}%`",
        "",
        "## Scientific limitations",
        "",
    ]
    for x in report["scientific_limitations"]:
        lines.append(f"- {x}")
    lines += [
        "",
        "This report is a calibration artifact. It must not be described as external validation.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(report, fitted_params, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    (out/"fit_result.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out/"optimized_parameters.json").write_text(
        json.dumps(fitted_params, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lock = {
        "software_version": __version__,
        "dataset_id": report["dataset_id"],
        "analysis_type": report["analysis_type"],
        "optimized_parameter_sha256": report["optimized_parameter_sha256"],
        "fit_parameters": report["fit_parameters"],
        "optimized_values": report["optimized_values"],
        "warning": "Use this lock for downstream validation; do not refit validation datasets.",
    }
    (out/"calibration_parameters.lock.json").write_text(
        json.dumps(lock, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    (out/"parameter_estimation_report.md").write_text(
        render_markdown(report), encoding="utf-8"
    )

    with (out/"optimization_trace.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["iteration", "objective", "rmse_residual"] + [f"x_{p}" for p in report["fit_parameters"]]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in report["trace"]:
            rr = {
                "iteration": row["iteration"],
                "objective": row["objective"],
                "rmse_residual": row["rmse_residual"],
            }
            for p, value in zip(report["fit_parameters"], row["x"]):
                rr[f"x_{p}"] = value
            w.writerow(rr)

    with (out/"fitted_predictions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dataset_id", "observable", "index", "observed", "predicted", "residual_model_minus_observed"])
        for obs, comp in report["comparisons_after_fit"].items():
            for i, (o, p, r) in enumerate(zip(comp["observed"], comp["predicted"], comp["residuals_model_minus_observed"])):
                w.writerow([report["dataset_id"], obs, i, o, p, r])

    files = [
        "fit_result.json", "optimized_parameters.json", "calibration_parameters.lock.json",
        "parameter_estimation_report.md", "optimization_trace.csv", "fitted_predictions.csv",
    ]
    manifest = {
        "analysis_type": "bounded_parameter_estimation",
        "dataset_id": report["dataset_id"],
        "inputs": {
            "data_sha256": report["data_sha256"],
            "metadata_sha256": report["metadata_sha256"],
            "initial_parameter_sha256": report["initial_parameter_sha256"],
        },
        "outputs": {},
    }
    for name in files:
        manifest["outputs"][name] = hashlib.sha256((out/name).read_bytes()).hexdigest()
    (out/"fit_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_dir")
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--preset", default="minimal_growth_ethanol", choices=sorted(PRESETS))
    ap.add_argument("--parameters", nargs="*", default=None)
    ap.add_argument("--max-nfev", type=int, default=120)
    ap.add_argument("--allow-validation-fit", action="store_true")
    args = ap.parse_args(argv)

    dataset = load_dataset_directory(args.dataset_dir)
    report, fitted_params = estimate_parameters(
        dataset,
        parameters=args.parameters,
        preset=args.preset,
        max_nfev=args.max_nfev,
        allow_validation_fit=args.allow_validation_fit,
    )
    out = Path(args.output_dir) if args.output_dir else Path(args.dataset_dir)/"fit_results"
    write_outputs(report, fitted_params, out)
    print(f"Parameter-estimation artifacts written to {out.resolve()}")
    print(f"Final integrity: {report['software_integrity_after_fit']['overall_status']}")
    print(f"Final objective: {report['final_objective']:.8g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

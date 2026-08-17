"""Generate deterministic sensitivity/practical-identifiability artifacts.

This module is headless. It supports either a nominal prior scenario or an
external dataset directory from the v2.5/v2.6 validation schema. In dataset mode,
the simulated horizon, initial conditions, observables and observation times are
taken from the dataset metadata/data, while parameters are still not fitted.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from biofermentor import __version__
from biofermentor.core import defaults
from biofermentor.sensitivity import (
    DEFAULT_PARAMETERS,
    DEFAULT_OUTPUTS,
    central_local_sensitivities,
    identifiability_diagnostics,
    step_robustness,
)
from biofermentor.validation_data import load_dataset_directory
from biofermentor.validation_data.runner import parameters_for_dataset
from biofermentor.validation_data.provenance import canonical_json_sha256

_OBS_TO_OUTPUT = {
    "X_g_L": "X_total",
    "S_g_L": "S",
    "P_g_L": "P",
    "N_g_L": "N",
    "DO_pct": "DO_pct",
}


def _jsonable(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    return x


def _finite_dataset_outputs(dataset):
    """Return model outputs corresponding to dataset observables with data."""
    outputs = []
    for obs in dataset.observable_columns:
        if obs in _OBS_TO_OUTPUT and np.any(np.isfinite(dataset.data[obs])):
            outputs.append(_OBS_TO_OUTPUT[obs])
    # preserve order and uniqueness
    seen = set()
    uniq = []
    for o in outputs:
        if o not in seen:
            uniq.append(o); seen.add(o)
    return tuple(uniq)


def build(parameters=None, outputs=None, rel_step=1e-3, tf_h=4.0, dt_h=0.02,
          dataset_dir=None):
    if dataset_dir is None:
        p = defaults()
        p["tf"] = float(tf_h)
        p["dt"] = float(dt_h)
        p["mode"] = "Batelada"
        pars = tuple(parameters or DEFAULT_PARAMETERS)
        outs = tuple(outputs or DEFAULT_OUTPUTS)
        obs_times = None
        scope = "nominal_batch_prior_to_parameter_estimation"
        dataset_info = None
    else:
        ds = load_dataset_directory(dataset_dir)
        p = parameters_for_dataset(ds)
        # Keep any user-provided dt if present in parameter_overrides; otherwise CLI dt.
        p["dt"] = float(p.get("dt", dt_h))
        pars = tuple(parameters or DEFAULT_PARAMETERS)
        outs = tuple(outputs or _finite_dataset_outputs(ds))
        obs_times = ds.time_h
        scope = "dataset_specific_prior_to_parameter_estimation"
        dataset_info = {
            "dataset_id": ds.dataset_id,
            "role": ds.role,
            "data_origin": ds.metadata["data_origin"],
            "data_sha256": ds.data_sha256,
            "metadata_sha256": ds.metadata_sha256,
        }

    s = central_local_sensitivities(pars, outs, rel_step, p, obs_times)
    d = identifiability_diagnostics(s)
    rob = step_robustness(pars, outs, (rel_step/2, rel_step, rel_step*2), p, obs_times)
    ranking = sorted(
        [
            {
                "parameter": pname,
                "rms_scaled_sensitivity": float(r),
                "peak_scaled_sensitivity": float(pk),
            }
            for pname, r, pk in zip(s["parameters"], s["rms"], s["peak"])
        ],
        key=lambda x: x["rms_scaled_sensitivity"],
        reverse=True,
    )

    return {
        "schema_version": "1.1",
        "software_version": __version__,
        "analysis_type": "local_sensitivity_and_practical_identifiability",
        "scope": scope,
        "dataset": dataset_info,
        "base_parameter_sha256": canonical_json_sha256(p),
        "settings": {
            "tf_h": float(p["tf"]),
            "dt_h": float(p["dt"]),
            "rel_step": float(rel_step),
            "parameters": list(pars),
            "outputs": list(outs),
            "n_observation_times": len(s["observation_times_h"]),
        },
        "ranking": ranking,
        "identifiability": {k: _jsonable(v) for k, v in d.items()},
        "finite_difference_step_robustness": rob,
        "scientific_limitations": [
            "This is local practical-identifiability screening, not structural-identifiability proof.",
            "Results depend on nominal parameters, experiment design, selected outputs and finite-difference step.",
            "A parameter should not be fitted solely because it ranks as sensitive.",
            "Dataset-specific sensitivity uses sampling times/observables, but still does not fit parameters.",
        ],
    }


def render_md(r):
    d = r["identifiability"]
    lines = [
        "# Sensitivity & Practical Identifiability Report",
        "",
        f"- Software: `{r['software_version']}`",
        f"- Analysis: `{r['analysis_type']}`",
        f"- Scope: `{r['scope']}`",
        f"- Parameter SHA-256: `{r['base_parameter_sha256']}`",
        f"- Outputs: `{', '.join(r['settings']['outputs'])}`",
        f"- Parameters tested: `{', '.join(r['settings']['parameters'])}`",
        f"- Observation times: `{r['settings']['n_observation_times']}`",
        f"- Numerical rank: **{d['numerical_rank']}/{d['n_parameters']}**",
        f"- Rank deficiency: **{d['rank_deficiency']}**",
        f"- Condition number: `{d['condition_number']:.6g}`",
        "",
    ]
    if r.get("dataset"):
        ds = r["dataset"]
        lines += [
            "## Dataset context",
            "",
            f"- Dataset: `{ds['dataset_id']}`",
            f"- Role: `{ds['role']}`",
            f"- Origin: `{ds['data_origin']}`",
            f"- Data SHA-256: `{ds['data_sha256']}`",
            f"- Metadata SHA-256: `{ds['metadata_sha256']}`",
            "",
        ]

    lines += [
        "## Sensitivity ranking",
        "",
        "| Rank | Parameter | RMS scaled sensitivity | Peak |",
        "|---:|---|---:|---:|",
    ]
    for i, x in enumerate(r["ranking"], 1):
        lines.append(
            f"| {i} | `{x['parameter']}` | {x['rms_scaled_sensitivity']:.6g} | {x['peak_scaled_sensitivity']:.6g} |"
        )

    lines += ["", "## Highly correlated parameter pairs", ""]
    if d["highly_correlated_pairs"]:
        lines += ["| Parameter 1 | Parameter 2 | cosine similarity |", "|---|---|---:|"]
        for x in d["highly_correlated_pairs"]:
            lines.append(
                f"| `{x['parameter_1']}` | `{x['parameter_2']}` | {x['cosine_similarity']:.6f} |"
            )
    else:
        lines.append("None above the configured threshold.")

    lines += [
        "", "## Low-sensitivity parameters", "",
        ", ".join(f"`{x}`" for x in d["low_sensitivity_parameters"]) or "None.",
        "", "## Conservative initial fit subset", "",
        ", ".join(f"`{x}`" for x in d["recommended_initial_fit_subset"]) or "None.",
        "", "## Interpretation", "",
        d["interpretation"], "",
        "This report is a screening diagnostic. It must not be cited as proof of structural identifiability.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default=".")
    ap.add_argument("--dataset-dir", default=None)
    ap.add_argument("--tf", type=float, default=4.0)
    ap.add_argument("--dt", type=float, default=0.01)
    ap.add_argument("--rel-step", type=float, default=1e-3)
    ap.add_argument("--parameters", nargs="*", default=None)
    ap.add_argument("--outputs", nargs="*", default=None)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)

    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    r = build(a.parameters, a.outputs, a.rel_step, a.tf, a.dt, a.dataset_dir)
    js = json.dumps(r, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    md = render_md(r)
    if a.check:
        ok = (out/"IDENTIFIABILITY_RESULTS.json").exists() and (out/"IDENTIFIABILITY_REPORT.md").exists()
        ok = ok and (out/"IDENTIFIABILITY_RESULTS.json").read_text(encoding="utf-8") == js
        ok = ok and (out/"IDENTIFIABILITY_REPORT.md").read_text(encoding="utf-8") == md
        print("IDENTIFIABILITY_REPORT_SYNC=PASS" if ok else "IDENTIFIABILITY_REPORT_SYNC=FAIL")
        return 0 if ok else 1

    (out/"IDENTIFIABILITY_RESULTS.json").write_text(js, encoding="utf-8")
    (out/"IDENTIFIABILITY_REPORT.md").write_text(md, encoding="utf-8")
    with (out/"SENSITIVITY_RANKING.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["parameter", "rms_scaled_sensitivity", "peak_scaled_sensitivity"])
        w.writeheader(); w.writerows(r["ranking"])
    print(f"Generated sensitivity/identifiability report for v{__version__} in {out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

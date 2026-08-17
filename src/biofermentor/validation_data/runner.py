import copy
import json
from pathlib import Path
import numpy as np

from biofermentor.core import defaults, BiofermentorSimulator
from .mapping import extract_model_series
from .metrics import comparison_metrics, residual_series, endpoint_error, aggregate_nrmse
from .provenance import canonical_json_sha256


_INITIAL_TO_PARAM = {
    "Xv0_g_L": "Xv0",
    "S0_g_L": "S0",
    "P0_g_L": "P0",
    "N0_g_L": "N0",
    "V0_L": "V0",
    "T0_C": "T0",
    "pH0": "pH0",
}


def parameters_for_dataset(dataset, base_parameters=None):
    p = copy.deepcopy(defaults() if base_parameters is None else base_parameters)
    exp = dataset.metadata["experiment"]
    p["mode"] = exp["mode"]
    p["tf"] = float(exp["tf_h"])

    for source_key, param_key in _INITIAL_TO_PARAM.items():
        p[param_key] = float(exp["initial_conditions"][source_key])

    overrides = exp.get("parameter_overrides", {})
    unknown = sorted(set(overrides) - set(p))
    if unknown:
        raise ValueError(f"Unknown parameter overrides: {unknown}")
    p.update(overrides)
    return p


def _interp_at_experimental_times(model_t, model_y, exp_t):
    return np.interp(exp_t, model_t, model_y)


def run_zero_fit_validation(dataset, base_parameters=None):
    """Run external comparison without parameter fitting."""
    p = parameters_for_dataset(dataset, base_parameters=base_parameters)
    result = BiofermentorSimulator(p).run()
    exp_t = dataset.time_h

    comparisons = {}
    for observable in dataset.observable_columns:
        spec = dataset.metadata["model_mapping"][observable]
        model_series = extract_model_series(result, spec)
        pred = _interp_at_experimental_times(result["t"], model_series, exp_t)
        obs = dataset.data[observable]
        comparisons[observable] = {
            "mapping": spec,
            "observed": [None if not np.isfinite(v) else float(v) for v in obs],
            "predicted": [float(v) for v in pred],
            "residuals_model_minus_observed": residual_series(obs, pred),
            "endpoint_error": endpoint_error(obs, pred),
            "metrics": comparison_metrics(obs, pred),
        }

    parameter_hash = canonical_json_sha256(p)
    aggregate = aggregate_nrmse(comparisons)
    return {
        "analysis_type": "zero_fit_external_comparison",
        "dataset_id": dataset.dataset_id,
        "dataset_role": dataset.role,
        "data_origin": dataset.metadata["data_origin"],
        "data_sha256": dataset.data_sha256,
        "metadata_sha256": dataset.metadata_sha256,
        "parameter_sha256": parameter_hash,
        "software_integrity": result["integrity_report"],
        "comparisons": comparisons,
        "aggregate_mean_NRMSE_range": aggregate,
        "scientific_interpretation": (
            "No parameters were fitted to this dataset. Metrics quantify a priori "
            "agreement under declared model mapping and experimental conditions."
        ),
    }

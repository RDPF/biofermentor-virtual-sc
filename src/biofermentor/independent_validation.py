"""Frozen-parameter independent-validation prediction layer.

v3.0 applies a previously generated calibration lock to an untouched validation
or external-replication dataset. No parameter fitting is performed here.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import numpy as np

from biofermentor.core import defaults, BiofermentorSimulator
from biofermentor.validation_data import ExperimentalDataset
from biofermentor.validation_data.runner import parameters_for_dataset
from biofermentor.validation_data.mapping import extract_model_series
from biofermentor.validation_data.metrics import comparison_metrics, residual_series, endpoint_error, aggregate_nrmse
from biofermentor.validation_data.provenance import sha256_file, canonical_json_sha256
from biofermentor.validation_data.qualification import qualification

ALLOWED_PREDICTION_ROLES = {"validation", "external_replication", "synthetic_demo"}

class IndependentValidationError(ValueError):
    pass


def load_calibration_lock(lock_path):
    lock_path = Path(lock_path)
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    required = {"analysis_type", "optimized_values", "optimized_parameter_sha256", "fit_parameters"}
    missing = sorted(required - set(lock))
    if missing:
        raise IndependentValidationError(f"Calibration lock is missing fields: {missing}")
    if lock["analysis_type"] != "bounded_parameter_estimation":
        raise IndependentValidationError("Calibration lock is not a bounded_parameter_estimation artifact")
    return lock


def parameters_from_lock_for_dataset(dataset, lock, base_parameters=None):
    p = parameters_for_dataset(dataset, base_parameters=base_parameters)
    unknown = sorted(set(lock["optimized_values"]) - set(p))
    if unknown:
        raise IndependentValidationError(f"Lock contains unknown parameter(s): {unknown}")
    for k, v in lock["optimized_values"].items():
        p[k] = float(v)
    return p


def ensure_predictable_dataset(dataset: ExperimentalDataset, allow_calibration_prediction=False):
    if dataset.role in ALLOWED_PREDICTION_ROLES:
        return
    if allow_calibration_prediction and dataset.role == "calibration":
        return
    raise IndependentValidationError(
        f"Refusing independent-validation prediction for dataset role {dataset.role!r}. "
        "Use role='validation' or 'external_replication'. Calibration sets are protected."
    )


def run_independent_validation(dataset, lock_path, base_parameters=None, allow_calibration_prediction=False):
    """Run a frozen-parameter prediction on a dataset without fitting."""
    ensure_predictable_dataset(dataset, allow_calibration_prediction=allow_calibration_prediction)
    lock_path = Path(lock_path)
    lock = load_calibration_lock(lock_path)
    p = parameters_from_lock_for_dataset(dataset, lock, base_parameters=base_parameters)
    result = BiofermentorSimulator(p).run()
    t = dataset.time_h

    comparisons = {}
    for obs in dataset.observable_columns:
        spec = dataset.metadata["model_mapping"][obs]
        model_series = extract_model_series(result, spec)
        pred = np.interp(t, result["t"], model_series)
        observed = dataset.data[obs]
        comparisons[obs] = {
            "mapping": spec,
            "observed": [None if not np.isfinite(v) else float(v) for v in observed],
            "predicted": [float(v) for v in pred],
            "residuals_model_minus_observed": residual_series(observed, pred),
            "endpoint_error": endpoint_error(observed, pred),
            "metrics": comparison_metrics(observed, pred),
        }

    report = {
        "analysis_type": "frozen_parameter_independent_prediction",
        "no_parameter_fitting_performed": True,
        "dataset_id": dataset.dataset_id,
        "dataset_role": dataset.role,
        "data_origin": dataset.metadata["data_origin"],
        "data_sha256": dataset.data_sha256,
        "metadata_sha256": dataset.metadata_sha256,
        "calibration_lock_path": str(lock_path),
        "calibration_lock_sha256": sha256_file(lock_path),
        "calibration_dataset_id": lock.get("dataset_id"),
        "optimized_parameter_sha256_from_lock": lock["optimized_parameter_sha256"],
        "prediction_parameter_sha256": canonical_json_sha256(p),
        "frozen_fit_parameters": list(lock["fit_parameters"]),
        "frozen_optimized_values": dict(lock["optimized_values"]),
        "software_integrity": result["integrity_report"],
        "dynamic_carbon": result["dynamic_carbon_audit"],
        "dynamic_nitrogen": result["dynamic_nitrogen_audit"],
        "dynamic_oxygen": result["dynamic_oxygen_audit"],
        "comparisons": comparisons,
        "aggregate_mean_NRMSE_range": aggregate_nrmse(comparisons),
        "scientific_interpretation": (
            "Frozen parameters from a prior calibration lock were applied to this dataset. "
            "No parameters were estimated from this dataset. If the dataset role/origin are real "
            "external evidence, this is an independent validation prediction."
        ),
        "scientific_limitations": [
            "Independent validation is only as strong as dataset provenance and the prior calibration lock.",
            "Synthetic datasets can test software behavior but cannot qualify as external experimental validation.",
            "Good metrics do not prove structural correctness outside the validated experimental domain.",
        ],
    }
    report["qualification"] = qualification(dataset, report)
    if report["qualification"]["status"] == "QUALIFIED" and dataset.role == "synthetic_demo":
        raise IndependentValidationError("Internal error: synthetic_demo cannot be QUALIFIED external validation")
    return report, p

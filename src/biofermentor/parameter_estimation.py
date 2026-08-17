"""Bounded parameter estimation for Biofermentor Virtual SC.

This module implements the bounded calibration layer used by the v3.0 model. It is headless and deliberately
separates calibration from validation. By default, only datasets declared as
`calibration` or `synthetic_demo` may be fitted.
"""
from __future__ import annotations

import copy
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from biofermentor.core import defaults, BiofermentorSimulator
from biofermentor.validation_data import ExperimentalDataset
from biofermentor.validation_data.mapping import extract_model_series
from biofermentor.validation_data.metrics import comparison_metrics, residual_series, aggregate_nrmse
from biofermentor.validation_data.provenance import canonical_json_sha256
from biofermentor.validation_data.runner import parameters_for_dataset


ALLOWED_FIT_ROLES = {"calibration", "synthetic_demo"}

# Conservative physiological/practical bounds. These are not universal truths;
# they are default priors meant to prevent numerically absurd fits.
PARAMETER_BOUNDS = {
    "mu_max": (0.02, 1.20),
    "Ks": (0.01, 50.0),
    "KiS": (20.0, 1000.0),
    "Kn": (0.001, 10.0),
    "Ko": (0.01, 20.0),
    "Pmax": (20.0, 200.0),
    "nP": (0.2, 6.0),
    "Yxs": (0.02, 0.80),
    "Yps": (0.05, 0.70),
    "Yxn": (2.0, 30.0),
    "ms": (0.0, 0.20),
    "qS_ng_max": (0.0, 3.0),
    "Ks_cat": (0.01, 100.0),
    "Kn_cat": (0.001, 10.0),
    "N_cat_floor": (0.0, 1.0),
    "N_uncouple_exp": (0.20, 5.0),
    "Kcrab": (0.05, 100.0),
    "w_crab": (0.0, 1.0),
    "kd0": (0.0, 0.10),
    "kd_eth": (0.0, 20.0),
}

PRESETS = {
    "minimal_growth_ethanol": ("mu_max", "Yxs", "Yps", "qS_ng_max"),
    "v27_recommended": ("Ko", "Yps", "Yxn", "Kcrab", "w_crab"),
    "v30_catabolic": ("qS_ng_max", "Kn_cat", "N_cat_floor", "Yps"),
    "ethanol_inhibition": ("mu_max", "Yxs", "Yps", "Pmax", "nP", "qS_ng_max"),
    "nitrogen_core": ("mu_max", "Yxs", "Yxn", "Kn", "qS_ng_max", "Kn_cat", "N_cat_floor"),
}


class ParameterEstimationError(ValueError):
    pass


def resolve_parameters(parameters=None, preset="minimal_growth_ethanol"):
    if parameters:
        pars = tuple(parameters)
    else:
        if preset not in PRESETS:
            raise ParameterEstimationError(f"Unknown fit preset: {preset}")
        pars = PRESETS[preset]
    unknown = [p for p in pars if p not in PARAMETER_BOUNDS]
    if unknown:
        raise ParameterEstimationError(f"No default bounds for parameter(s): {unknown}")
    return tuple(pars)


def bounds_for(parameters, custom_bounds=None):
    custom_bounds = custom_bounds or {}
    lo, hi = [], []
    for name in parameters:
        b = custom_bounds.get(name, PARAMETER_BOUNDS[name])
        if len(b) != 2 or not (float(b[0]) < float(b[1])):
            raise ParameterEstimationError(f"Invalid bounds for {name}: {b}")
        lo.append(float(b[0])); hi.append(float(b[1]))
    return np.array(lo, float), np.array(hi, float)


def ensure_fittable_dataset(dataset: ExperimentalDataset, allow_validation_fit=False):
    if allow_validation_fit:
        return
    if dataset.role not in ALLOWED_FIT_ROLES:
        raise ParameterEstimationError(
            f"Refusing to fit dataset role {dataset.role!r}. "
            "Use only role='calibration' for real calibration. Validation datasets "
            "must remain untouched."
        )


def objective_scale(observed):
    y = np.asarray(observed, dtype=float)
    finite = y[np.isfinite(y)]
    if finite.size < 2:
        return 1.0
    r = float(np.max(finite) - np.min(finite))
    if r > 1e-12:
        return r
    m = float(np.max(np.abs(finite)))
    return m if m > 1e-12 else 1.0


def simulation_comparisons(dataset, params):
    result = BiofermentorSimulator(params).run()
    exp_t = dataset.time_h
    comps = {}
    for obs in dataset.observable_columns:
        spec = dataset.metadata["model_mapping"][obs]
        model_series = extract_model_series(result, spec)
        pred = np.interp(exp_t, result["t"], model_series)
        observed = dataset.data[obs]
        comps[obs] = {
            "mapping": spec,
            "observed": [None if not np.isfinite(v) else float(v) for v in observed],
            "predicted": [float(v) for v in pred],
            "residuals_model_minus_observed": residual_series(observed, pred),
            "metrics": comparison_metrics(observed, pred),
            "scale": objective_scale(observed),
        }
    return result, comps


def residual_vector(dataset, params, weights=None):
    _, comps = simulation_comparisons(dataset, params)
    weights = weights or {}
    pieces = []
    for obs, comp in comps.items():
        w = float(weights.get(obs, 1.0))
        obs_arr = np.array([np.nan if v is None else v for v in comp["observed"]], float)
        pred_arr = np.array(comp["predicted"], float)
        mask = np.isfinite(obs_arr) & np.isfinite(pred_arr)
        if np.any(mask):
            scale = max(float(comp["scale"]), 1e-12)
            pieces.append(math.sqrt(w) * (pred_arr[mask] - obs_arr[mask]) / scale)
    if not pieces:
        raise ParameterEstimationError("No finite observed/model pairs for objective.")
    return np.concatenate(pieces)


def _set_params(base, names, values):
    p = copy.deepcopy(base)
    for name, value in zip(names, values):
        p[name] = float(value)
    return p


def _scipy_least_squares(fun, x0, lb, ub, max_nfev, trace):
    from scipy.optimize import least_squares

    def wrapped(x):
        r = fun(x)
        trace.append({
            "iteration": len(trace),
            "x": [float(v) for v in x],
            "objective": float(np.sum(r*r)),
            "rmse_residual": float(np.sqrt(np.mean(r*r))),
        })
        return r

    res = least_squares(
        wrapped, x0, bounds=(lb, ub), max_nfev=max_nfev,
        xtol=1e-8, ftol=1e-8, gtol=1e-8,
    )
    return {
        "x": res.x,
        "success": bool(res.success),
        "message": str(res.message),
        "nfev": int(res.nfev),
        "cost": float(res.cost),
        "optimizer": "scipy.optimize.least_squares",
        "raw_status": int(res.status),
    }


def _coordinate_fallback(fun, x0, lb, ub, max_nfev, trace):
    """Small deterministic fallback if SciPy is unavailable."""
    x = np.clip(np.array(x0, float), lb, ub)
    r = fun(x); best = float(np.sum(r*r))
    trace.append({"iteration": 0, "x": [float(v) for v in x], "objective": best,
                  "rmse_residual": float(np.sqrt(np.mean(r*r)))})
    step = 0.25*(ub-lb)
    nfev = 1
    improved = True
    while nfev < max_nfev and np.max(step) > 1e-6 and improved:
        improved = False
        for j in range(len(x)):
            for direction in (-1.0, 1.0):
                cand = x.copy()
                cand[j] = np.clip(cand[j] + direction*step[j], lb[j], ub[j])
                rr = fun(cand); obj = float(np.sum(rr*rr)); nfev += 1
                trace.append({
                    "iteration": len(trace), "x": [float(v) for v in cand],
                    "objective": obj, "rmse_residual": float(np.sqrt(np.mean(rr*rr)))
                })
                if obj < best:
                    x, best, improved = cand, obj, True
                if nfev >= max_nfev:
                    break
            if nfev >= max_nfev:
                break
        step *= 0.5
    return {
        "x": x,
        "success": True,
        "message": "coordinate-search fallback completed",
        "nfev": nfev,
        "cost": 0.5*best,
        "optimizer": "deterministic_coordinate_search_fallback",
        "raw_status": 0,
    }


def estimate_parameters(dataset, parameters=None, preset="minimal_growth_ethanol",
                        base_parameters=None, custom_bounds=None, weights=None,
                        max_nfev=120, allow_validation_fit=False):
    ensure_fittable_dataset(dataset, allow_validation_fit=allow_validation_fit)
    names = resolve_parameters(parameters, preset)
    base = parameters_for_dataset(dataset, base_parameters=base_parameters)
    lb, ub = bounds_for(names, custom_bounds)

    x0 = np.array([float(base[n]) for n in names], float)
    x0 = np.clip(x0, lb, ub)

    trace = []

    def fun(x):
        p = _set_params(base, names, x)
        return residual_vector(dataset, p, weights=weights)

    r0 = fun(x0)
    initial_obj = float(np.sum(r0*r0))
    t0 = time.time()
    try:
        opt = _scipy_least_squares(fun, x0, lb, ub, max_nfev, trace)
    except ImportError:
        opt = _coordinate_fallback(fun, x0, lb, ub, max_nfev, trace)

    elapsed = time.time() - t0

    fitted_params = _set_params(base, names, opt["x"])
    initial_result, initial_comps = simulation_comparisons(dataset, base)
    fitted_result, fitted_comps = simulation_comparisons(dataset, fitted_params)

    report = {
        "analysis_type": "bounded_parameter_estimation",
        "dataset_id": dataset.dataset_id,
        "dataset_role": dataset.role,
        "data_origin": dataset.metadata["data_origin"],
        "data_sha256": dataset.data_sha256,
        "metadata_sha256": dataset.metadata_sha256,
        "fit_parameters": list(names),
        "bounds": {n: [float(a), float(b)] for n, a, b in zip(names, lb, ub)},
        "initial_values": {n: float(v) for n, v in zip(names, x0)},
        "optimized_values": {n: float(v) for n, v in zip(names, opt["x"])},
        "initial_parameter_sha256": canonical_json_sha256(base),
        "optimized_parameter_sha256": canonical_json_sha256(fitted_params),
        "initial_objective": initial_obj,
        "final_objective": float(2.0*opt["cost"]),
        "objective_reduction_factor": (
            None if opt["cost"] <= 0 else float(initial_obj / max(2.0*opt["cost"], 1e-300))
        ),
        "optimizer": {
            "name": opt["optimizer"],
            "success": opt["success"],
            "message": opt["message"],
            "nfev": opt["nfev"],
            "raw_status": opt["raw_status"],
            "elapsed_s": float(elapsed),
        },
        "initial_metrics": {k: v["metrics"] for k, v in initial_comps.items()},
        "fitted_metrics": {k: v["metrics"] for k, v in fitted_comps.items()},
        "initial_aggregate_mean_NRMSE_range": aggregate_nrmse(initial_comps),
        "fitted_aggregate_mean_NRMSE_range": aggregate_nrmse(fitted_comps),
        "software_integrity_after_fit": fitted_result["integrity_report"],
        "dynamic_carbon_after_fit": fitted_result["dynamic_carbon_audit"],
        "dynamic_nitrogen_after_fit": fitted_result["dynamic_nitrogen_audit"],
        "dynamic_oxygen_after_fit": fitted_result["dynamic_oxygen_audit"],
        "comparisons_after_fit": fitted_comps,
        "trace": trace,
        "scientific_limitations": [
            "This is calibration, not independent validation.",
            "Validation datasets must remain untouched and should be evaluated only with frozen optimized parameters.",
            "Parameter estimates are local and depend on bounds, observable mapping, weights and initial values.",
            "Passing C/N/O2 integrity audits is necessary but not sufficient for biological validity.",
        ],
    }
    return report, fitted_params

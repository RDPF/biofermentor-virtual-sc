import pytest

from biofermentor.validation_data import load_dataset_directory
from biofermentor.parameter_estimation import (
    estimate_parameters,
    resolve_parameters,
    bounds_for,
    ParameterEstimationError,
)


def test_resolve_parameter_preset():
    pars = resolve_parameters(preset="minimal_growth_ethanol")
    assert pars == ("mu_max", "Yxs", "Yps", "qS_ng_max")
    lo, hi = bounds_for(pars)
    assert len(lo) == len(pars)
    assert all(lo < hi)


def test_parameter_estimation_reduces_synthetic_objective(project_root):
    ds = load_dataset_directory(
        project_root / "validation" / "datasets" / "synthetic_calibration_v30"
    )
    report, fitted = estimate_parameters(
        ds,
        preset="minimal_growth_ethanol",
        max_nfev=80,
    )
    assert report["optimizer"]["success"]
    assert report["final_objective"] < report["initial_objective"]
    assert report["fitted_aggregate_mean_NRMSE_range"] < report["initial_aggregate_mean_NRMSE_range"]
    assert report["software_integrity_after_fit"]["overall_status"] in {"PASS", "WARNING"}
    for p in report["fit_parameters"]:
        lo, hi = report["bounds"][p]
        assert lo <= report["optimized_values"][p] <= hi


def test_refuses_to_fit_validation_role(tmp_path):
    md = {
        "schema_version": "1.0",
        "dataset_id": "validation_must_not_fit",
        "title": "validation",
        "role": "validation",
        "data_origin": "synthetic",
        "license": "test",
        "source": {"citation": "test"},
        "experiment": {
            "mode": "Batelada",
            "tf_h": 1.0,
            "initial_conditions": {
                "Xv0_g_L": 1.0,
                "S0_g_L": 10.0,
                "P0_g_L": 0.0,
                "N0_g_L": 0.5,
                "V0_L": 1.0,
                "T0_C": 30.0,
                "pH0": 5.0
            }
        },
        "model_mapping": {"X_g_L": {"model_variable": "X_total"}}
    }
    (tmp_path/"metadata.json").write_text(__import__("json").dumps(md), encoding="utf-8")
    (tmp_path/"data.csv").write_text("time_h,X_g_L\n0,1\n1,1.2\n", encoding="utf-8")
    ds = load_dataset_directory(tmp_path)
    with pytest.raises(ParameterEstimationError):
        estimate_parameters(ds, parameters=["mu_max"], max_nfev=5)

from biofermentor.validation_data import (
    load_dataset_directory,
    run_zero_fit_validation,
)


def test_synthetic_zero_fit_pipeline_is_reproducible(project_root):
    ds = load_dataset_directory(
        project_root / "validation" / "datasets" / "synthetic_demo"
    )
    a = run_zero_fit_validation(ds)
    b = run_zero_fit_validation(ds)
    assert a == b
    assert a["analysis_type"] == "zero_fit_external_comparison"
    assert a["dataset_role"] == "synthetic_demo"
    # Synthetic demo is generated from the same model and should match closely.
    assert a["comparisons"]["X_g_L"]["metrics"]["RMSE"] < 1e-8
    assert a["comparisons"]["P_g_L"]["metrics"]["RMSE"] < 1e-8

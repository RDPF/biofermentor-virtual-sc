from biofermentor.validation_data import load_dataset_directory, run_zero_fit_validation

def test_zero_fit_report_contains_residuals_and_aggregate(project_root):
    ds = load_dataset_directory(project_root/"validation"/"datasets"/"synthetic_demo")
    r = run_zero_fit_validation(ds)
    assert "aggregate_mean_NRMSE_range" in r
    for comp in r["comparisons"].values():
        assert len(comp["residuals_model_minus_observed"]) == len(ds.time_h)
        assert "endpoint_error" in comp

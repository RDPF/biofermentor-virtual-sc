from biofermentor.validation_data import load_dataset_directory
from biofermentor.parameter_estimation import estimate_parameters


def test_parameter_estimation_report_contains_required_audits(project_root):
    ds = load_dataset_directory(
        project_root / "validation" / "datasets" / "synthetic_calibration_v30"
    )
    report, _ = estimate_parameters(ds, parameters=["mu_max"], max_nfev=20)
    assert "dynamic_carbon_after_fit" in report
    assert "dynamic_nitrogen_after_fit" in report
    assert "dynamic_oxygen_after_fit" in report
    assert "comparisons_after_fit" in report
    assert "scientific_limitations" in report
    assert any("calibration" in s.lower() for s in report["scientific_limitations"])

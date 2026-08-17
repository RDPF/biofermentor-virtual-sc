import pytest

from biofermentor.validation_data import load_dataset_directory
from biofermentor.independent_validation import (
    run_independent_validation,
    IndependentValidationError,
)


def test_frozen_parameter_independent_prediction_synthetic_exp3(project_root):
    ds = load_dataset_directory(project_root / 'validation' / 'datasets' / 'synthetic_exp3_validation_v30')
    lock = project_root / 'validation' / 'reports' / 'synthetic_calibration_v30_fit' / 'calibration_parameters.lock.json'
    report, params = run_independent_validation(ds, lock)
    assert report['no_parameter_fitting_performed'] is True
    assert report['analysis_type'] == 'frozen_parameter_independent_prediction'
    assert report['qualification']['status'] == 'NOT_QUALIFIED'
    assert report['aggregate_mean_NRMSE_range'] < 1e-8
    assert report['software_integrity']['overall_status'] == 'PASS'
    for name in ['mu_max','Yxs','Yps','qS_ng_max']:
        assert params[name] == pytest.approx(report['frozen_optimized_values'][name])


def test_independent_validation_refuses_calibration_dataset(project_root):
    ds = load_dataset_directory(project_root / 'validation' / 'datasets' / 'synthetic_calibration_v30')
    lock = project_root / 'validation' / 'reports' / 'synthetic_calibration_v30_fit' / 'calibration_parameters.lock.json'
    with pytest.raises(IndependentValidationError):
        run_independent_validation(ds, lock)

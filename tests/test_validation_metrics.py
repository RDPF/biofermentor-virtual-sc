import pytest
from biofermentor.validation_data.metrics import comparison_metrics


def test_perfect_prediction_metrics():
    m = comparison_metrics([1,2,3,4], [1,2,3,4])
    assert m["RMSE"] == pytest.approx(0.0)
    assert m["MAE"] == pytest.approx(0.0)
    assert m["MBE"] == pytest.approx(0.0)
    assert m["R2"] == pytest.approx(1.0)
    assert m["NRMSE_range"] == pytest.approx(0.0)


def test_metrics_ignore_missing_observations():
    m = comparison_metrics([1.0, float("nan"), 3.0], [1.0, 2.0, 2.5])
    assert m["n"] == 2

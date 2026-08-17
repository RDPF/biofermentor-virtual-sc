from biofermentor.core import defaults
from biofermentor.core.validation import _status_from_abs_error


def test_mass_balance_status_boundaries():
    p = defaults()
    assert _status_from_abs_error(0.0, p) == "PASS"
    assert _status_from_abs_error(5.0, p) == "PASS"
    assert _status_from_abs_error(5.01, p) == "WARNING"
    assert _status_from_abs_error(9.99, p) == "WARNING"
    assert _status_from_abs_error(10.0, p) == "FAIL"


def test_invalid_mass_balance_thresholds_fail_loudly():
    p = defaults()
    p["mass_balance_fail_abs_error_pct"] = p["mass_balance_pass_abs_error_pct"]
    try:
        _status_from_abs_error(1.0, p)
    except ValueError:
        return
    raise AssertionError("Expected ValueError for invalid thresholds")

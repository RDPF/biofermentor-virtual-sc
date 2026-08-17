import pytest
from biofermentor.core import defaults
from biofermentor.core.validation import parameter_consistency_audit


def test_default_parameter_audit_has_known_status():
    a = parameter_consistency_audit(defaults())
    assert a["status"] in {"PASS", "WARNING"}


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("Yps", 1.5),
        ("Yco2s_ferm", 2.5),
        ("Yco2s_resp", 3.0),
    ],
)
def test_parameter_audit_warns_for_deliberately_inconsistent_yields(field, bad_value):
    p = defaults()
    p[field] = bad_value
    a = parameter_consistency_audit(p)
    assert a["status"] == "WARNING"
    assert a["warnings"]

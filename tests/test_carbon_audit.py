import math
from biofermentor.core import defaults, BiofermentorSimulator
from biofermentor.core.validation import parameter_consistency_audit

def test_parameter_audit_is_explicitly_static():
    p = defaults()
    a = parameter_consistency_audit(p)
    assert a["scope"] == "parameter_plausibility_only"
    assert math.isfinite(a["carbon_recovery_nominal_ferm"])
    assert math.isfinite(a["carbon_recovery_nominal_resp"])

def test_dynamic_carbon_audit_is_finite_and_reported():
    p = defaults()
    p["tf"] = 6.0
    p["dt"] = 0.01
    r = BiofermentorSimulator(p).run()
    a = r["dynamic_carbon_audit"]
    for key in ["carbon_in_gC","accounted_gC","residual_gC","error_pct","recovery_pct"]:
        assert math.isfinite(a[key]), (key, a)
    assert a["carbon_in_gC"] > 0
    assert a["status"] in {"PASS", "WARNING", "FAIL"}

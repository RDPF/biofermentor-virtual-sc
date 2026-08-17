import math
from biofermentor.core import defaults, BiofermentorSimulator


def test_dynamic_nitrogen_audit_is_finite_and_classified():
    p = defaults()
    p["tf"] = 8.0
    p["dt"] = 0.01
    r = BiofermentorSimulator(p).run()
    a = r["dynamic_nitrogen_audit"]
    for key in [
        "nitrogen_in_gN", "accounted_gN", "residual_gN",
        "error_pct", "recovery_pct"
    ]:
        assert math.isfinite(a[key]), (key, a)
    assert a["nitrogen_in_gN"] > 0
    assert a["status"] in {"PASS", "WARNING", "FAIL"}


def test_integrity_report_contains_both_elemental_balances():
    p = defaults()
    p["tf"] = 4.0
    p["dt"] = 0.01
    r = BiofermentorSimulator(p).run()
    rep = r["integrity_report"]
    assert rep["overall_status"] in {"PASS", "WARNING", "FAIL"}
    assert rep["carbon_status"] in {"PASS", "WARNING", "FAIL"}
    assert rep["nitrogen_status"] in {"PASS", "WARNING", "FAIL"}

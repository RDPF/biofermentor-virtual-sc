import math
import copy

from biofermentor.core import defaults, BiofermentorSimulator
from biofermentor.core.validation import dynamic_oxygen_audit


def test_dynamic_oxygen_audit_is_finite_and_passes_reference_case():
    p = defaults()
    p["tf"] = 8.0
    p["dt"] = 0.0025
    r = BiofermentorSimulator(p).run()
    a = r["dynamic_oxygen_audit"]
    for key in [
        "initial_dissolved_mgO2", "transferred_mgO2", "consumed_mgO2",
        "final_dissolved_mgO2", "residual_mgO2", "error_pct", "recovery_pct",
    ]:
        assert math.isfinite(a[key]), (key, a)
    assert a["status"] == "PASS"


def test_oxygen_audit_detects_deliberately_corrupted_our_trajectory():
    p = defaults()
    p["tf"] = 4.0
    p["dt"] = 0.0025
    r = BiofermentorSimulator(p).run()
    bad = dict(r)
    bad["A"] = r["A"].copy()
    bad["A"][:, 6] *= 2.0  # corrupt OUR while leaving state trajectory unchanged
    a = dynamic_oxygen_audit(bad, p)
    assert a["status"] in {"WARNING", "FAIL"}
    assert abs(a["error_pct"]) > p["mass_balance_pass_abs_error_pct"]

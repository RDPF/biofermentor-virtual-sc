from biofermentor.core import defaults
from biofermentor.core.process import SCProcess
from biofermentor.core.validation import physiological_self_tests

def test_all_physiological_semantics():
    p = defaults()
    checks = physiological_self_tests(SCProcess(p), p)
    assert checks, "No physiological tests executed"
    assert all(checks.values()), checks

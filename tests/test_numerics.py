from biofermentor.core import defaults, BiofermentorSimulator
from biofermentor.core.validation import numerical_self_tests

def test_representative_numerical_cases():
    report = numerical_self_tests(BiofermentorSimulator, defaults)
    failed = {
        case: [name for name, ok in checks.items() if not ok]
        for case, checks in report.items()
        if not all(checks.values())
    }
    assert not failed, failed

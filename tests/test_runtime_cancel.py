import pytest
from biofermentor.core import defaults, BiofermentorSimulator, SimulationCancelled


def test_progress_callback_reaches_completion():
    p = defaults()
    p["tf"] = 1.0
    p["dt"] = 0.01
    seen = []
    BiofermentorSimulator(p).run(
        progress_callback=lambda fraction, t: seen.append((fraction, t))
    )
    assert seen
    assert seen[-1][0] == pytest.approx(1.0)


def test_cooperative_cancellation():
    p = defaults()
    p["tf"] = 4.0
    p["dt"] = 0.01
    calls = {"n": 0}

    def cancel():
        calls["n"] += 1
        return calls["n"] > 10

    with pytest.raises(SimulationCancelled):
        BiofermentorSimulator(p).run(cancel_check=cancel)

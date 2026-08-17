import numpy as np
import pytest
from biofermentor.core import defaults
from biofermentor.core.process import SCProcess


def _y(p, volume=None):
    return np.array([
        p["Xv0"], p["Xd0"], p["S0"], p["P0"], p["N0"], p["CL0"],
        p["V0"] if volume is None else volume,
        p["T0"], p["pH0"], p["Foam0"], p["Pr0"]
    ], float)


def _kla(p, rpm, gas, volume=None):
    proc = SCProcess(p)
    u = dict(
        feed=0.0, acid=0.0, base=0.0, antifoam=0.0,
        rpm=rpm, gas=gas, o2frac=p["o2_base"], vent=0.2, heat=0.0
    )
    proc.rhs(0.0, _y(p, volume), u)
    return proc.aux["kla"]


@pytest.mark.parametrize("rpm1,rpm2", [(200.0, 400.0), (400.0, 800.0)])
def test_kla_increases_with_rpm(rpm1, rpm2):
    p = defaults()
    assert _kla(p, rpm2, 0.8) > _kla(p, rpm1, 0.8)


@pytest.mark.parametrize("g1,g2", [(0.2, 0.5), (0.5, 1.2)])
def test_kla_increases_with_gas_flow(g1, g2):
    p = defaults()
    assert _kla(p, 500.0, g2) > _kla(p, 500.0, g1)


def test_kla_decreases_with_volume_for_negative_volume_exponent():
    p = defaults()
    assert p["kla_v"] < 0
    assert _kla(p, 500.0, 0.8, volume=4.0) < _kla(p, 500.0, 0.8, volume=2.0)

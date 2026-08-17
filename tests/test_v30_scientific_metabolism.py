import numpy as np

from biofermentor.core import defaults, SCProcess, BiofermentorSimulator


def test_nitrogen_exhaustion_does_not_zero_catabolic_fermentation():
    p = defaults()
    y = np.array([5.5, 0.1, 60.0, 12.0, 0.0, 2.0, 2.0, 30.0, 5.0, 0.0, 0.1])
    k = SCProcess(p).kinetics(y)
    assert k["mu"] < 1e-10
    assert k["qS_ng"] > 0.10
    assert k["qP"] > 0.02
    assert k["n_stress"] > 0.99


def test_nitrogen_limitation_recruits_non_growth_catabolism():
    p = defaults()
    base = np.array([5.0, 0.0, 40.0, 10.0, 0.5, 3.0, 2.0, 30.0, 5.0, 0.0, 0.1])
    low_n = base.copy(); low_n[4] = 0.002
    kh = SCProcess(p).kinetics(base)
    kl = SCProcess(p).kinetics(low_n)
    assert kl["mu"] < kh["mu"]
    assert kl["qS_ng"] > kh["qS_ng"]
    assert kl["n_uncoupling"] > kh["n_uncoupling"]


def test_original_high_sugar_low_n_case_keeps_fermenting_after_n_depletion():
    p = defaults()
    p.update(mode="Batelada", S0=90.0, N0=0.45, tf=20.0, dt=0.0025)
    r = BiofermentorSimulator(p).run()
    i6 = int(np.argmin(np.abs(r["t"] - 6.0)))
    i20 = int(np.argmin(np.abs(r["t"] - 20.0)))
    assert r["Y"][i6, 4] < 1e-3
    assert r["Y"][i20, 3] - r["Y"][i6, 3] > 5.0
    assert r["Y"][i6, 2] - r["Y"][i20, 2] > 10.0


def test_v30_default_recipe_is_operationally_bounded():
    r = BiofermentorSimulator(defaults()).run()
    assert not r["trip"]
    assert r["Y"][-1, 2] < 15.0
    assert r["Y"][-1, 3] > 30.0
    assert r["Y"][-1, 6] < defaults()["V_HH"]
    assert r["dynamic_carbon_audit"]["status"] == "PASS"
    assert r["dynamic_nitrogen_audit"]["status"] == "PASS"
    assert r["dynamic_oxygen_audit"]["status"] == "PASS"

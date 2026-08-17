import numpy as np
from biofermentor.sensitivity import identifiability_diagnostics

def test_identifiability_detects_collinear_columns():
    fake={
        "matrix":np.array([[1.,2.,0.],[2.,4.,1.],[3.,6.,0.]]),
        "parameters":("a","b","c"),
        "rms":np.array([2.0,4.0,0.6]),
    }
    d=identifiability_diagnostics(fake,corr_threshold=0.999)
    pairs={(x["parameter_1"],x["parameter_2"]) for x in d["highly_correlated_pairs"]}
    assert ("a","b") in pairs
    assert d["rank_deficiency"] >= 1

def test_identifiability_detects_low_sensitivity():
    fake={
        "matrix":np.array([[1.,1e-8],[2.,2e-8],[3.,3e-8]]),
        "parameters":("strong","weak"),
        "rms":np.array([2.0,2e-8]),
    }
    d=identifiability_diagnostics(fake,low_sensitivity_ratio=1e-3)
    assert "weak" in d["low_sensitivity_parameters"]

def test_report_explicitly_disclaims_structural_identifiability():
    fake={"matrix":np.eye(2),"parameters":("a","b"),"rms":np.ones(2)}
    d=identifiability_diagnostics(fake)
    assert "not establish structural identifiability" in d["interpretation"]

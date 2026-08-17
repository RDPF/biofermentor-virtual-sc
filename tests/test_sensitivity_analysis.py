import numpy as np
from biofermentor.core import defaults
from biofermentor.sensitivity import central_local_sensitivities

def _small():
    p=defaults(); p["tf"]=2.0; p["dt"]=0.02; p["mode"]="Batelada"
    return p

def test_sensitivity_matrix_is_finite_and_shaped():
    s=central_local_sensitivities(["mu_max","Ks","Yxs"],["X_total","S","P"],1e-3,_small())
    assert s["matrix"].shape[1] == 3
    assert np.all(np.isfinite(s["matrix"]))
    assert np.all(s["rms"] >= 0)

def test_mu_max_has_nonzero_growth_sensitivity():
    s=central_local_sensitivities(["mu_max"],["X_total"],1e-3,_small())
    assert s["rms"][0] > 0

def test_central_difference_step_is_reasonably_stable():
    a=central_local_sensitivities(["mu_max"],["X_total"],5e-4,_small())
    b=central_local_sensitivities(["mu_max"],["X_total"],1e-3,_small())
    rel=abs(a["rms"][0]-b["rms"][0])/max(abs(b["rms"][0]),1e-12)
    assert rel < 0.05

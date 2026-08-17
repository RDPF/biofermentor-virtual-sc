import numpy as np
from biofermentor.core import defaults
from biofermentor.core.process import SCProcess

def test_batch_rhs_has_zero_volume_derivative_when_no_feed():
    p = defaults()
    proc = SCProcess(p)
    y = np.array([p["Xv0"],p["Xd0"],p["S0"],p["P0"],p["N0"],p["CL0"],
                  p["V0"],p["T0"],p["pH0"],p["Foam0"],p["Pr0"]],float)
    u = dict(feed=0.0,acid=0.0,base=0.0,antifoam=0.0,rpm=p["rpm_base"],
             gas=p["gas_base"],o2frac=p["o2_base"],vent=0.2,heat=0.0)
    dy = proc.rhs(0.0,y,u)
    assert abs(dy[6]) < 1e-15

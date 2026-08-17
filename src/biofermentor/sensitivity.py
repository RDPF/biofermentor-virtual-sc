"""Local sensitivity and practical-identifiability diagnostics.

The implementation is deliberately headless and uses central finite differences
around a declared nominal parameter vector. Sensitivities are scaled to be
dimensionless:

    S_ij = (theta_j / scale_i) * d y_i / d theta_j

where scale_i is the observed/model trajectory range (with a robust fallback).
This is a *local practical-identifiability* diagnostic, not a proof of structural
identifiability.
"""
from __future__ import annotations
import copy
import numpy as np

from biofermentor.core import defaults, BiofermentorSimulator

DEFAULT_PARAMETERS = (
    "mu_max", "Ks", "KiS", "Kn", "Ko", "Pmax", "nP",
    "Yxs", "Yps", "Yxn", "ms",
    "qS_ng_max", "Ks_cat", "Kn_cat", "N_cat_floor", "N_uncouple_exp",
    "Kcrab", "w_crab", "kd0", "kd_eth",
)

DEFAULT_OUTPUTS = ("X_total", "S", "P", "N", "DO_pct")

def _series(result, name):
    if name == "X_total": return result["Y"][:,0] + result["Y"][:,1]
    if name == "Xv": return result["Y"][:,0]
    if name == "S": return result["Y"][:,2]
    if name == "P": return result["Y"][:,3]
    if name == "N": return result["Y"][:,4]
    if name == "DO_pct": return result["M"][:,2]
    raise KeyError(name)

def _scale(y):
    y=np.asarray(y,float)
    r=float(np.nanmax(y)-np.nanmin(y))
    if r > 1e-12: return r
    m=float(np.nanmax(np.abs(y)))
    return m if m > 1e-12 else 1.0

def central_local_sensitivities(parameters=None, outputs=None, rel_step=1e-3,
                                base_parameters=None, observation_times=None):
    if rel_step <= 0:
        raise ValueError("rel_step must be positive")
    pars=tuple(parameters or DEFAULT_PARAMETERS)
    outs=tuple(outputs or DEFAULT_OUTPUTS)
    p0=copy.deepcopy(defaults() if base_parameters is None else base_parameters)
    nominal=BiofermentorSimulator(p0).run()
    model_t=np.asarray(nominal["t"],float)
    if observation_times is None:
        t=model_t
    else:
        t=np.asarray(observation_times,dtype=float)
        if t.ndim != 1 or len(t) < 2:
            raise ValueError("observation_times must be a 1-D array with at least two points")
        if np.any(np.diff(t) <= 0):
            raise ValueError("observation_times must be strictly increasing")
        if t[0] < model_t[0]-1e-12 or t[-1] > model_t[-1]+1e-12:
            raise ValueError("observation_times must lie inside simulated time horizon")

    def sample(result, output):
        y=_series(result,output)
        if observation_times is None:
            return y
        return np.interp(t, result["t"], y)

    nominal_series={o:sample(nominal,o) for o in outs}
    scales={o:_scale(nominal_series[o]) for o in outs}
    sens=np.zeros((len(t)*len(outs),len(pars)),float)

    for j,name in enumerate(pars):
        if name not in p0:
            raise KeyError(f"Unknown parameter {name!r}")
        theta=float(p0[name])
        # Relative perturbation should scale with the parameter itself. Using a
        # unit floor makes a nominal 1e-3 step disproportionately large for
        # sub-unit kinetic constants and can cross controller/event boundaries.
        h=rel_step*abs(theta) if abs(theta)>1e-12 else rel_step
        pp=copy.deepcopy(p0); pm=copy.deepcopy(p0)
        pp[name]=theta+h
        pm[name]=theta-h
        # Positive-domain kinetic constants/yields cannot cross zero.
        if theta > 0 and pm[name] <= 0:
            pm[name]=theta
            pp[name]=theta+h
            denom=h
            rp=BiofermentorSimulator(pp).run()
            rm=nominal
        else:
            denom=pp[name]-pm[name]
            rp=BiofermentorSimulator(pp).run()
            rm=BiofermentorSimulator(pm).run()

        blocks=[]
        for o in outs:
            dy=(sample(rp,o)-sample(rm,o))/denom
            # Dimensionless sensitivity. For theta=0, use h as local scale.
            theta_scale=abs(theta) if abs(theta)>1e-12 else h
            blocks.append(theta_scale*dy/scales[o])
        sens[:,j]=np.concatenate(blocks)

    rms=np.sqrt(np.mean(sens**2,axis=0))
    peak=np.max(np.abs(sens),axis=0)
    return {
        "time_h": t,
        "parameters": pars,
        "outputs": outs,
        "matrix": sens,
        "rms": rms,
        "peak": peak,
        "nominal": nominal,
        "scales": scales,
        "rel_step": float(rel_step),
        "observation_times_h": t,
    }

def identifiability_diagnostics(sensitivity_result, svd_tol=1e-8,
                                corr_threshold=0.95, low_sensitivity_ratio=1e-3):
    S=np.asarray(sensitivity_result["matrix"],float)
    pars=sensitivity_result["parameters"]
    rms=np.asarray(sensitivity_result["rms"],float)

    # Remove rows with no information.
    informative=np.linalg.norm(S,axis=1)>1e-14
    A=S[informative,:]
    if A.size == 0:
        singular=np.zeros(len(pars))
        rank=0
        cond=float("inf")
        corr=np.eye(len(pars))
    else:
        singular=np.linalg.svd(A,compute_uv=False)
        if singular.size and singular[0] > 0:
            rank=int(np.sum(singular > svd_tol*singular[0]))
            cond=float("inf") if singular[-1] <= 0 else float(singular[0]/singular[-1])
        else:
            rank=0; cond=float("inf")
        # Parameter-column correlation/cosine similarity.
        norms=np.linalg.norm(A,axis=0)
        corr=np.eye(len(pars))
        for i in range(len(pars)):
            for j in range(i+1,len(pars)):
                if norms[i] == 0 or norms[j] == 0:
                    c=0.0
                else:
                    c=float(np.dot(A[:,i],A[:,j])/(norms[i]*norms[j]))
                corr[i,j]=corr[j,i]=c

    max_rms=float(np.max(rms)) if rms.size else 0.0
    low=[]
    if max_rms>0:
        low=[pars[i] for i,v in enumerate(rms) if v < low_sensitivity_ratio*max_rms]
    correlated=[]
    for i in range(len(pars)):
        for j in range(i+1,len(pars)):
            if abs(corr[i,j]) >= corr_threshold:
                correlated.append({
                    "parameter_1": pars[i],
                    "parameter_2": pars[j],
                    "cosine_similarity": float(corr[i,j]),
                })

    # Conservative recommendation: sensitive parameters not involved in very
    # strong collinearity. This is a screening set, not a definitive fit set.
    involved={x["parameter_1"] for x in correlated}|{x["parameter_2"] for x in correlated}
    recommended=[p for p in pars if p not in low and p not in involved]

    return {
        "method": "local_scaled_sensitivity_SVD_and_column_cosine_screening",
        "interpretation": (
            "Practical/local screening only; does not establish structural identifiability."
        ),
        "numerical_rank": rank,
        "n_parameters": len(pars),
        "rank_deficiency": len(pars)-rank,
        "singular_values": [float(x) for x in singular],
        "condition_number": cond,
        "correlation_matrix": corr,
        "low_sensitivity_parameters": low,
        "highly_correlated_pairs": correlated,
        "recommended_initial_fit_subset": recommended,
        "thresholds": {
            "svd_relative_tol": svd_tol,
            "absolute_cosine_similarity": corr_threshold,
            "low_sensitivity_ratio_to_max_rms": low_sensitivity_ratio,
        },
    }

def step_robustness(parameters=None, outputs=None, steps=(5e-4,1e-3,2e-3),
                    base_parameters=None, observation_times=None):
    results=[]
    for h in steps:
        s=central_local_sensitivities(parameters,outputs,h,base_parameters,observation_times)
        results.append(s)
    rms=np.vstack([r["rms"] for r in results])
    ref=rms[len(results)//2]
    denom=np.maximum(np.abs(ref),1e-12)
    rel=np.max(np.abs(rms-ref)/denom,axis=0)
    return {
        "steps":[float(x) for x in steps],
        "parameters":list(results[0]["parameters"]),
        "max_relative_rms_deviation":[float(x) for x in rel],
    }

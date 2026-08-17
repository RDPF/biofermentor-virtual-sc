import math
import numpy as np


def _paired(obs, pred):
    obs = np.asarray(obs, dtype=float)
    pred = np.asarray(pred, dtype=float)
    mask = np.isfinite(obs) & np.isfinite(pred)
    return obs[mask], pred[mask]


def comparison_metrics(observed, predicted):
    y, yh = _paired(observed, predicted)
    if y.size < 2:
        return {
            "n": int(y.size),
            "RMSE": None,
            "MAE": None,
            "NRMSE_range": None,
            "R2": None,
            "MBE": None,
        }

    e = yh - y
    rmse = float(np.sqrt(np.mean(e**2)))
    mae = float(np.mean(np.abs(e)))
    mbe = float(np.mean(e))
    yrange = float(np.max(y) - np.min(y))
    nrmse = None if yrange <= 0 else rmse / yrange
    sse = float(np.sum(e**2))
    sst = float(np.sum((y - np.mean(y))**2))
    r2 = None if sst <= 0 else 1.0 - sse/sst

    return {
        "n": int(y.size),
        "RMSE": rmse,
        "MAE": mae,
        "NRMSE_range": None if nrmse is None else float(nrmse),
        "R2": None if r2 is None else float(r2),
        "MBE": mbe,
    }


def residual_series(observed, predicted):
    obs = np.asarray(observed, dtype=float)
    pred = np.asarray(predicted, dtype=float)
    out = []
    for o, p in zip(obs, pred):
        if np.isfinite(o) and np.isfinite(p):
            out.append(float(p - o))
        else:
            out.append(None)
    return out


def endpoint_error(observed, predicted):
    obs = np.asarray(observed, dtype=float)
    pred = np.asarray(predicted, dtype=float)
    mask = np.isfinite(obs) & np.isfinite(pred)
    if not np.any(mask):
        return None
    idx = np.where(mask)[0][-1]
    return float(pred[idx] - obs[idx])


def aggregate_nrmse(comparisons):
    vals = []
    for c in comparisons.values():
        v = c["metrics"].get("NRMSE_range")
        if v is not None and np.isfinite(v):
            vals.append(float(v))
    return None if not vals else float(np.mean(vals))

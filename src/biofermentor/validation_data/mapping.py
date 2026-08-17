import numpy as np


MODEL_VARIABLES = {
    "Xv": lambda result: result["Y"][:, 0],
    "Xd": lambda result: result["Y"][:, 1],
    "X_total": lambda result: result["Y"][:, 0] + result["Y"][:, 1],
    "S": lambda result: result["Y"][:, 2],
    "P": lambda result: result["Y"][:, 3],
    "N": lambda result: result["Y"][:, 4],
    "DO_pct": lambda result: result["M"][:, 2],
}


def extract_model_series(result, mapping_spec):
    """Extract a model trajectory from a declarative mapping specification.

    Supported forms:
      {"model_variable": "X_total"}
      {"model_variable": "Xv"}
      {"model_variable": "S"}
      ...
    """
    key = mapping_spec.get("model_variable")
    if key not in MODEL_VARIABLES:
        raise ValueError(f"Unsupported model_variable mapping: {key!r}")
    return np.asarray(MODEL_VARIABLES[key](result), dtype=float)

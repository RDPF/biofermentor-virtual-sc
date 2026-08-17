"""Canonical external-validation schema."""

SCHEMA_VERSION = "1.0"

# Canonical data columns. time_h is required; scientific observables are optional
# but at least one must be present.
CANONICAL_COLUMNS = {
    "time_h": {"unit": "h", "required": True},
    "X_g_L": {"unit": "g/L", "required": False},
    "S_g_L": {"unit": "g/L", "required": False},
    "P_g_L": {"unit": "g/L", "required": False},
    "N_g_L": {"unit": "g/L", "required": False},
    "DO_pct": {"unit": "% saturation", "required": False},
}

OBSERVABLE_COLUMNS = ("X_g_L", "S_g_L", "P_g_L", "N_g_L", "DO_pct")

ALLOWED_DATASET_ROLES = {
    "calibration",
    "validation",
    "external_replication",
    "synthetic_demo",
}

ALLOWED_DATA_ORIGINS = {
    "original_open_data",
    "supplementary_information",
    "digitized_from_figure",
    "synthetic",
}

REQUIRED_METADATA_FIELDS = {
    "dataset_id",
    "title",
    "role",
    "data_origin",
    "license",
    "source",
    "experiment",
    "model_mapping",
}

REQUIRED_EXPERIMENT_FIELDS = {
    "mode",
    "tf_h",
    "initial_conditions",
}

REQUIRED_INITIAL_CONDITIONS = {
    "Xv0_g_L",
    "S0_g_L",
    "P0_g_L",
    "N0_g_L",
    "V0_L",
    "T0_C",
    "pH0",
}

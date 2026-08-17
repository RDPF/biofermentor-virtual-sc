import json
from pathlib import Path
import pytest

from biofermentor.validation_data import (
    load_dataset_directory,
    ValidationDatasetError,
)


def test_synthetic_demo_dataset_loads(project_root):
    ds = load_dataset_directory(
        project_root / "validation" / "datasets" / "synthetic_demo"
    )
    assert ds.role == "synthetic_demo"
    assert ds.metadata["data_origin"] == "synthetic"
    assert "X_g_L" in ds.observable_columns


def test_dataset_rejects_non_monotonic_time(tmp_path):
    md = {
        "schema_version": "1.0",
        "dataset_id": "bad_time",
        "title": "bad",
        "role": "validation",
        "data_origin": "synthetic",
        "license": "internal-test",
        "source": {"citation": "test"},
        "experiment": {
            "mode": "Batelada",
            "tf_h": 2.0,
            "initial_conditions": {
                "Xv0_g_L": 1.0, "S0_g_L": 10.0, "P0_g_L": 0.0,
                "N0_g_L": 0.5, "V0_L": 2.0, "T0_C": 30.0, "pH0": 5.0
            }
        },
        "model_mapping": {"X_g_L": {"model_variable": "X_total"}}
    }
    (tmp_path/"metadata.json").write_text(json.dumps(md), encoding="utf-8")
    (tmp_path/"data.csv").write_text("time_h,X_g_L\n0,1\n2,2\n1,3\n", encoding="utf-8")
    with pytest.raises(ValidationDatasetError):
        load_dataset_directory(tmp_path)


def test_digitized_dataset_requires_digitization_metadata(tmp_path):
    md = {
        "schema_version": "1.0",
        "dataset_id": "digit_bad",
        "title": "bad",
        "role": "validation",
        "data_origin": "digitized_from_figure",
        "license": "test",
        "source": {"citation": "test"},
        "experiment": {
            "mode": "Batelada", "tf_h": 2.0,
            "initial_conditions": {
                "Xv0_g_L": 1.0, "S0_g_L": 10.0, "P0_g_L": 0.0,
                "N0_g_L": 0.5, "V0_L": 2.0, "T0_C": 30.0, "pH0": 5.0
            }
        },
        "model_mapping": {"X_g_L": {"model_variable": "X_total"}}
    }
    (tmp_path/"metadata.json").write_text(json.dumps(md), encoding="utf-8")
    (tmp_path/"data.csv").write_text("time_h,X_g_L\n0,1\n1,2\n", encoding="utf-8")
    with pytest.raises(ValidationDatasetError):
        load_dataset_directory(tmp_path)

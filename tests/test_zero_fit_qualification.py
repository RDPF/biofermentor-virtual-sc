from biofermentor.validation_data import (
    load_dataset_directory,
    run_zero_fit_validation,
    qualification,
)

def test_synthetic_demo_cannot_be_claimed_as_external_validation(project_root):
    ds = load_dataset_directory(project_root/"validation"/"datasets"/"synthetic_demo")
    r = run_zero_fit_validation(ds)
    q = qualification(ds, r)
    assert q["status"] == "NOT_QUALIFIED"
    assert not q["qualified_external_validation"]

def test_external_role_and_origin_can_qualify(tmp_path):
    import json
    md = {
        "schema_version": "1.0",
        "dataset_id": "external_test",
        "title": "External test",
        "role": "validation",
        "data_origin": "supplementary_information",
        "license": "CC BY 4.0",
        "source": {"citation": "Author et al.", "doi": "10.1234/example"},
        "experiment": {
            "mode": "Batelada", "tf_h": 1.0,
            "initial_conditions": {
                "Xv0_g_L": 1.0, "S0_g_L": 10.0, "P0_g_L": 0.0,
                "N0_g_L": 0.5, "V0_L": 1.0, "T0_C": 30.0, "pH0": 5.0
            }
        },
        "model_mapping": {"X_g_L": {"model_variable": "X_total"}}
    }
    (tmp_path/"metadata.json").write_text(json.dumps(md), encoding="utf-8")
    (tmp_path/"data.csv").write_text("time_h,X_g_L\n0,1\n1,1.1\n", encoding="utf-8")
    ds = load_dataset_directory(tmp_path)
    q = qualification(ds)
    assert q["status"] == "QUALIFIED"

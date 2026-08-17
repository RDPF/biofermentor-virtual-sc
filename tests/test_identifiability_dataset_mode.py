import os, sys, subprocess, json
from biofermentor.identifiability_report import build


def test_dataset_specific_identifiability_uses_dataset_times(project_root):
    r = build(dataset_dir=project_root/"validation"/"datasets"/"synthetic_demo",
              parameters=["mu_max","Yxs","Yps"], rel_step=1e-3)
    assert r["scope"] == "dataset_specific_prior_to_parameter_estimation"
    assert r["dataset"]["dataset_id"] == "synthetic_demo_v30"
    assert r["settings"]["n_observation_times"] == 9
    assert r["settings"]["outputs"]


def test_identifiability_cli_dataset_mode(project_root, tmp_path):
    env=os.environ.copy(); env["PYTHONPATH"]=str(project_root/"src")
    cmd=[sys.executable,"-m","biofermentor.identifiability_report",
         "--dataset-dir",str(project_root/"validation"/"datasets"/"synthetic_demo"),
         "--output-dir",str(tmp_path),"--parameters","mu_max","Yxs","Yps"]
    p=subprocess.run(cmd,cwd=project_root,env=env,capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    data=json.loads((tmp_path/"IDENTIFIABILITY_RESULTS.json").read_text(encoding="utf-8"))
    assert data["scope"] == "dataset_specific_prior_to_parameter_estimation"
    assert data["dataset"]["data_origin"] == "synthetic"

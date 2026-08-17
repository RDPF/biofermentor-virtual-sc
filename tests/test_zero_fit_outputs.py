import json
import os
import subprocess
import sys

def test_zero_fit_cli_writes_predictions_and_manifest(project_root, tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root/"src")
    p = subprocess.run(
        [sys.executable, "-m", "biofermentor.external_validation",
         str(project_root/"validation"/"datasets"/"synthetic_demo"),
         "--output-dir", str(tmp_path)],
        cwd=project_root, env=env, capture_output=True, text=True
    )
    assert p.returncode == 0, p.stderr
    assert (tmp_path/"zero_fit_predictions.csv").exists()
    assert (tmp_path/"baseline_manifest.json").exists()
    m = json.loads((tmp_path/"baseline_manifest.json").read_text(encoding="utf-8"))
    assert m["qualification"]["status"] == "NOT_QUALIFIED"
    assert len(m["outputs"]["zero_fit_report.json"]) == 64

import json
import os
import subprocess
import sys


def test_parameter_estimation_cli_outputs(project_root, tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "src")
    p = subprocess.run(
        [
            sys.executable, "-m", "biofermentor.parameter_estimation_report",
            str(project_root / "validation" / "datasets" / "synthetic_calibration_v30"),
            "--output-dir", str(tmp_path),
            "--preset", "minimal_growth_ethanol",
            "--max-nfev", "60",
        ],
        cwd=project_root,
        env=env,
        text=True,
        capture_output=True,
    )
    assert p.returncode == 0, p.stderr
    for name in [
        "fit_result.json",
        "optimized_parameters.json",
        "calibration_parameters.lock.json",
        "parameter_estimation_report.md",
        "optimization_trace.csv",
        "fitted_predictions.csv",
        "fit_manifest.json",
    ]:
        assert (tmp_path/name).exists(), name

    result = json.loads((tmp_path/"fit_result.json").read_text(encoding="utf-8"))
    assert result["analysis_type"] == "bounded_parameter_estimation"
    assert result["final_objective"] < result["initial_objective"]

    lock = json.loads((tmp_path/"calibration_parameters.lock.json").read_text(encoding="utf-8"))
    assert lock["optimized_parameter_sha256"] == result["optimized_parameter_sha256"]

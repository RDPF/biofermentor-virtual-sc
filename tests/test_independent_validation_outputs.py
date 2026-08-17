import json
import os
import subprocess
import sys


def test_independent_validation_cli_outputs(project_root, tmp_path):
    env = os.environ.copy(); env['PYTHONPATH'] = str(project_root / 'src')
    lock = project_root / 'validation' / 'reports' / 'synthetic_calibration_v30_fit' / 'calibration_parameters.lock.json'
    ds = project_root / 'validation' / 'datasets' / 'synthetic_exp3_validation_v30'
    p = subprocess.run([
        sys.executable, '-m', 'biofermentor.independent_validation_report', str(ds),
        '--calibration-lock', str(lock), '--output-dir', str(tmp_path)
    ], cwd=project_root, env=env, text=True, capture_output=True)
    assert p.returncode == 0, p.stderr
    for name in ['independent_validation_report.json','independent_validation_report.md','independent_validation_predictions.csv','independent_validation_manifest.json']:
        assert (tmp_path/name).exists(), name
    r=json.loads((tmp_path/'independent_validation_report.json').read_text(encoding='utf-8'))
    assert r['no_parameter_fitting_performed'] is True
    assert r['aggregate_mean_NRMSE_range'] < 1e-8
    m=json.loads((tmp_path/'independent_validation_manifest.json').read_text(encoding='utf-8'))
    assert m['no_parameter_fitting_performed'] is True
    assert len(m['inputs']['calibration_lock_sha256']) == 64

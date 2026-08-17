# Reproducibility guide

## Environment

Biofermentor Virtual SC requires Python 3.10 or newer. The headless scientific
core depends on NumPy; test/analysis workflows additionally use SciPy, pytest and
PyYAML. The GUI is optional and uses Tkinter plus Matplotlib.

## Minimal verification

From a clean checkout:

```bash
python -m pip install -e ".[test]"
python -m biofermentor.cli --self-test
pytest -q
python -m biofermentor.validation_report --output-dir . --check
python -m biofermentor.identifiability_report --output-dir . --check
```

For the GUI:

```bash
python -m pip install -e ".[gui]"
biofermentor-gui
```

## Release-manifest verification

`RELEASE_MANIFEST.json` inventories every tracked file in the release snapshot
except the manifest itself and records byte count plus SHA-256. A release archive
should be considered intact only if those hashes match.

## Dataset provenance

Synthetic datasets are labeled as synthetic and exist for regression and workflow
testing. Literature-target directories contain provenance and protocols even when
real observations are not distributable or not yet incorporated.

The pending real Exp. 3/calibration work is not part of v3.0.0. Do not substitute
synthetic values, digitized guesses or undocumented reconstructions for missing
experimental data.

## Frozen-parameter validation principle

When real calibration and validation data become available in a later release,
the intended sequence is: calibrate on the declared calibration set, write a
parameter lock, freeze it, and evaluate a distinct validation set without refitting.
That future work should receive its own versioned release and archived DOI.

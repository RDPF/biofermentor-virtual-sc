# Biofermentor Virtual SC

**Version 3.0.0 — Scientific Metabolism Decoupling**

Biofermentor Virtual SC is an open, auditable virtual fermentation platform for
*Saccharomyces cerevisiae* ethanol process-control studies. It combines a
phenomenological dynamic model, C/N/O₂ integrity audits, zero-fit comparison,
local sensitivity and practical-identifiability diagnostics, bounded parameter
estimation, and frozen-parameter independent-validation workflows.

## Scientific scope

This software is a transparent **phenomenological educational/research simulator**.
It is not a validated digital twin of a specific strain, vessel, medium or scale.
Automated C/N/O₂ audits and reproducible reports test model and numerical
consistency; they do **not** replace experimental validation.

The current public workflow is:

```text
zero-fit comparison
  → sensitivity + practical-identifiability screening
  → bounded parameter estimation on calibration datasets
  → frozen-parameter prediction on untouched validation datasets
```

The repository includes synthetic datasets for software smoke testing. These are
explicitly marked as synthetic and are never qualified as external-validation
evidence.

### Release boundary for v3.0.0

The non-growth-associated catabolic parameters introduced in v3.0.0 are
**phenomenological reference values, not experimentally calibrated constants**.
Consequently, this release is a structurally motivated research simulator and
reproducible software baseline, not a quantitatively validated model of a
particular *S. cerevisiae* strain or industrial fermentation.

Real-data calibration and the pending real Exp. 3 validation track — including
the Caicedo-Ortega experimental work discussed for a future calibration stage —
are intentionally **outside the scope of v3.0.0**. They should be handled in a
subsequent scientific release with its own archived DOI. No missing experimental
points are fabricated, digitized without provenance, or inferred in this release.


## v3.0 scientific model change

v3.0 removes the previous structural shortcut in which nitrogen exhaustion
forced nearly all glucose uptake and ethanol formation to collapse with growth.
The model now separates growth-associated substrate demand from a bounded
non-growth-associated catabolic flux (`qS_ng`) that can remain active during
nitrogen limitation. Nitrogen stress is reported explicitly but does not
automatically become cell death. The default fed-batch recipe is now S-stat
controlled and the reference RK4 step is 0.0025 h.

See [`SCIENTIFIC_MODEL_V3.md`](SCIENTIFIC_MODEL_V3.md) for equations, parameter
status, literature anchors and limitations. The new catabolic parameters are
phenomenological reference values and require experimental calibration for
quantitative use.

## Repository guide

Start here depending on your goal:

- **Scientific equations and assumptions:** [`SCIENTIFIC_MODEL_V3.md`](SCIENTIFIC_MODEL_V3.md)
- **What changed scientifically in v3.0.0:** [`V3_SCIENTIFIC_CHANGE_REPORT.md`](V3_SCIENTIFIC_CHANGE_REPORT.md)
- **Release verification:** [`V3_RELEASE_VERIFICATION.md`](V3_RELEASE_VERIFICATION.md)
- **Scientific status and claim boundaries:** [`docs/SCIENTIFIC_STATUS.md`](docs/SCIENTIFIC_STATUS.md)
- **Reproducibility:** [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md)
- **Repository structure:** [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md)
- **GitHub + Zenodo publication procedure:** [`docs/RELEASE_AND_ARCHIVING.md`](docs/RELEASE_AND_ARCHIVING.md)
- **Public-release verification:** [`docs/PUBLIC_RELEASE_VERIFICATION.md`](docs/PUBLIC_RELEASE_VERIFICATION.md)
- **Contribution policy:** [`CONTRIBUTING.md`](CONTRIBUTING.md)

## Installation

For the scientific core and tests:

```bash
python -m pip install -e ".[test]"
pytest -q
```

For the optional Tkinter/Matplotlib GUI:

```bash
python -m pip install -e ".[gui]"
biofermentor-gui
```

The source checkout can also be started directly with `python run_gui.py`. The
v3.0.0 interface uses a responsive vector P&ID, a visible in-canvas TRIP banner,
a structured alarm table, improved scientific plots, a resizable parameter
sidebar, and notebook-screen-aware startup sizing. Useful shortcuts are
`Ctrl+Enter` (simulate), `Ctrl+O` (open recipe), `Ctrl+S` (save recipe),
`Ctrl+E` (export CSV), and `Esc` (cancel a running simulation).

Tkinter itself is supplied by the Python/operating-system installation.

## Main command-line tools

```bash
biofermentor --self-test
biofermentor-validation-report --output-dir .
biofermentor-external-validation validation/datasets/synthetic_demo
biofermentor-identifiability --output-dir .
biofermentor-fit validation/datasets/synthetic_calibration_v30
biofermentor-independent-validation validation/datasets/synthetic_exp3_validation_v30 \
  --calibration-lock validation/reports/synthetic_calibration_v30_fit/calibration_parameters.lock.json
```

Equivalent module invocations are also supported, for example:

```bash
python -m biofermentor.cli --self-test
python -m biofermentor.validation_report --output-dir . --check
```

## Key outputs

The release contains reproducible machine-readable and human-readable artifacts:

```text
VALIDATION_REPORT.md / validation_results.json
IDENTIFIABILITY_REPORT.md / IDENTIFIABILITY_RESULTS.json
PARAMETER_ESTIMATION_REPORT.md / PARAMETER_ESTIMATION_RESULTS.json
INDEPENDENT_VALIDATION_REPORT.md / INDEPENDENT_VALIDATION_RESULTS.json
RELEASE_MANIFEST.json
```

Each analysis records data, metadata and parameter SHA-256 hashes whenever
applicable.

## Validation-data format

External datasets use a canonical directory layout:

```text
dataset_id/
  metadata.json
  data.csv
```

Canonical observables are:

```text
time_h, X_g_L, S_g_L, P_g_L, N_g_L, DO_pct
```

`time_h` is required. Experimental provenance, license, role, origin, initial
conditions and model-variable mappings are recorded in `metadata.json`.

## Current literature-validation target

The repository contains a scaffold for Valencia-Velásquez et al. (2025), DOI
`10.1007/s00449-025-03222-5`, including a protocol for zero-fit and independent
Exp. 3 validation. The real Exp. 3 time series is **not** included yet; no
experimental points have been fabricated.

## Development and CI

The GitHub Actions workflow validates:

- workflow YAML syntax;
- scientific self-test;
- pytest suite;
- headless core import without Tkinter/Matplotlib;
- validation-report synchronization;
- zero-fit infrastructure;
- practical-identifiability report synchronization;
- parameter-estimation smoke test;
- frozen-parameter independent-validation smoke test.

Local quick check:

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/tests.yml'))"
pytest -q
python -m biofermentor.validation_report --output-dir . --check
python -m biofermentor.identifiability_report --output-dir . --check
```

## How to cite

`CITATION.cff` is provided for GitHub's **Cite this repository** interface.
`.zenodo.json` contains the metadata intended for Zenodo release archiving.
For the public v3.0.0 release, cite the version-specific Zenodo DOI assigned
after the GitHub release is archived. Until that DOI exists, cite the software
name, author and version from `CITATION.cff`.

Do not invent or pre-fill a DOI in this source tree. After Zenodo assigns the
real DOI, it can be added to the default branch for discoverability without
rewriting or retagging the archived `v3.0.0` source snapshot.

## License

BSD-3-Clause. See `LICENSE`.

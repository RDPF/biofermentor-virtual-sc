# Public-release preparation verification — v3.0.0

This document records checks performed while reorganizing the already-verified
v3.0.0 scientific baseline for public GitHub and Zenodo release.

## Scope of this preparation

No files under `src/` or `tests/` were changed. `run_gui.py` and
`run_self_test.py` were also left unchanged. The public-release preparation is
limited to repository organization, release metadata, discoverability,
contribution templates, documentation and the SHA-256 manifest.

## Checks

- `src/`: byte-identical to the verified v3.0.0 baseline — PASS
- `tests/`: byte-identical to the verified v3.0.0 baseline — PASS
- launch scripts: byte-identical — PASS
- `.zenodo.json`: valid JSON and required release fields present — PASS
- `CITATION.cff`: valid YAML/CFF structure for the existing project metadata — PASS
- GitHub Actions and issue-template YAML parse — PASS
- scientific self-test — PASS
- validation-report synchronization check — PASS
- identifiability-report synchronization check — PASS
- focused metadata/headless/v3.0 scientific-regression tests: 8/8 — PASS
- explicit phenomenological/non-calibrated caveat in Zenodo description — PASS
- explicit real-data calibration / real Exp. 3 scope boundary — PASS

The underlying v3.0.0 scientific source and complete 63-test suite are unchanged
from the previously verified baseline. This preparation therefore does not create
new scientific behavior or a new calibration claim.

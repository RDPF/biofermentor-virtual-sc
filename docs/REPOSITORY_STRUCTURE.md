# Repository structure

The public repository deliberately keeps the scientific source, tests, release
metadata and reproducibility artifacts together so that a tagged release can be
archived as a self-contained research-software object.

```text
.
├── src/biofermentor/              Python package
│   ├── core/                      scientific model, controls, simulator, audits
│   └── gui/                       optional Tkinter/Matplotlib interface
├── tests/                         automated scientific/software regression tests
├── examples/                      minimal headless usage example
├── validation/
│   ├── datasets/                  canonical synthetic/test datasets
│   ├── literature/                provenance/protocol material for real literature targets
│   └── reports/                   generated and historical validation/calibration artifacts
├── docs/                          release, reproducibility and scientific-status guides
├── .github/
│   ├── workflows/                 continuous integration
│   └── ISSUE_TEMPLATE/            public issue forms
├── README.md                      public entry point
├── SCIENTIFIC_MODEL_V3.md         current model equations and limitations
├── V3_SCIENTIFIC_CHANGE_REPORT.md scientific v2.x → v3.0 regression summary
├── V3_RELEASE_VERIFICATION.md     release verification record
├── CHANGELOG.md                   version history
├── CITATION.cff                   GitHub citation metadata
├── .zenodo.json                   Zenodo/GitHub archival metadata
├── LICENSE                        BSD-3-Clause
├── pyproject.toml                 Python packaging and entry points
└── RELEASE_MANIFEST.json          SHA-256 inventory of the release snapshot
```

## Why historical artifacts remain

Some files under `validation/reports/` were produced by earlier software versions.
They are intentionally retained to preserve provenance and to avoid rewriting
scientific history. Current v3.0 artifacts are labeled with v3.0 dataset/report
identifiers; older artifacts must not be presented as validation of the v3.0 model.

## Generated CI artifacts

CI may create additional report directories locally during testing. These are
execution products, not new scientific evidence. Only explicitly versioned release
artifacts should be interpreted as part of the published scientific record.

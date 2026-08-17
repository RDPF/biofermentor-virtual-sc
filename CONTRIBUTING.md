# Contributing

Contributions are welcome when they preserve the project's scientific auditability.

## Before opening a pull request

1. Explain whether the change is software-only, GUI-only, numerical, or scientific.
2. For scientific-model changes, document the equation/assumption being changed,
   its rationale, parameter status and expected observable consequences.
3. Add or update regression tests for changed behavior.
4. Run:

```bash
python -m pip install -e ".[test]"
python -m biofermentor.cli --self-test
pytest -q
```

5. Do not label synthetic data as experimental validation.
6. Do not add undocumented real experimental data or data with unclear redistribution rights.

## Scientific claim discipline

A good numerical fit is not, by itself, validation. Parameter estimation,
identifiability, mass-balance audits and external prediction answer different
questions and should remain distinguishable in code and documentation.

The v3.0 non-growth-associated catabolic parameters are currently phenomenological
reference values. A future calibration contribution must identify the dataset,
provenance, observables, fitted subset, bounds, objective function and untouched
validation set.

## Versioning

Bug fixes and documentation changes should not silently change scientific model
semantics. Any change that alters the model equations, default physiological
interpretation or calibrated parameter set should be treated as a scientific
release and documented in `CHANGELOG.md`.

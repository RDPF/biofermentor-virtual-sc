## Change type

- [ ] Documentation/release metadata only
- [ ] GUI/software behavior only
- [ ] Numerical method
- [ ] Scientific model/parameter semantics
- [ ] Calibration/validation workflow

## Summary

Describe the change and why it is needed.

## Scientific impact

If scientific behavior changes, state the affected equations/parameters, rationale,
and expected observable consequences. If none, write “None”.

## Verification

- [ ] `python -m biofermentor.cli --self-test`
- [ ] `pytest -q`
- [ ] Relevant reports/manifests updated
- [ ] Synthetic data are not described as experimental evidence

# Biofermentor Virtual SC v3.0.0 — Scientific Metabolism Decoupling

Biofermentor Virtual SC v3.0.0 is the first release in the project to explicitly
separate growth-associated substrate demand from a bounded non-growth-associated
fermentative catabolic flux under nitrogen limitation.

## Scientific change

The v2.x structure could drive glucose uptake and ethanol formation close to zero
when nitrogen depletion stopped growth. v3.0.0 introduces an explicit `qS_ng`
pathway so nitrogen limitation can suppress biomass growth without forcing
fermentative catabolism to vanish by construction. Nitrogen stress is diagnosed
separately and is not automatically converted into cell death.

## Reference operation

The default fed-batch scenario now uses S-stat control and a revised bounded
working-volume configuration. The GUI exposes the new substrate-flux decomposition
and nitrogen-stress diagnostic.

## Reproducibility

The release includes C/N/O₂ audits, scientific regression tests, local sensitivity
and practical-identifiability diagnostics, bounded parameter estimation, synthetic
calibration/validation-like workflow tests, frozen-parameter independent-prediction
infrastructure and a SHA-256 release manifest.

## Scientific limitation — read before reuse

The new non-growth-associated catabolic parameters are **phenomenological reference
values and are not calibrated** to a specific *S. cerevisiae* strain, medium, vessel
or industrial process. v3.0.0 is therefore a structurally motivated research
simulator and reproducible baseline, not a quantitatively validated digital twin.
Synthetic datasets included with the release are software/workflow tests, not
experimental validation evidence.

Real-data calibration and the pending real Exp. 3 validation track are intentionally
out of scope for v3.0.0 and are reserved for a later scientific release with its
own archived DOI.

See `SCIENTIFIC_MODEL_V3.md`, `V3_SCIENTIFIC_CHANGE_REPORT.md` and
`docs/SCIENTIFIC_STATUS.md` for the scientific scope and limitations.

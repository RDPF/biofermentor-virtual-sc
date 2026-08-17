# Changelog

## 3.0.0 — Scientific Metabolism Decoupling

- Decoupled nitrogen-limited alcoholic catabolism from biomass growth by adding a non-growth-associated glucose flux (`qS_ng`).
- Added bounded nitrogen modulation of catabolic capacity (`Kn_cat`, `N_cat_floor`) and an explicit nitrogen-stress diagnostic.
- Kept nitrogen uptake growth-associated; nitrogen stress does not automatically imply cell death.
- Split substrate demand into growth, non-growth catabolism, maintenance, fermentative and respiratory fluxes and expose them in simulator auxiliary outputs/CSV.
- Replaced the reference exponential open-loop feed with an S-stat PID reference recipe and moved the nominal working-volume limit below the HH trip threshold.
- Reduced the reference RK4 step to 0.0025 h after oxygen-balance convergence checks for the v3.0 dynamics.
- Extended GUI metabolism controls, online N/stress display and kinetic plots for the new flux decomposition.
- Extended sensitivity and bounded-estimation parameter spaces with v3.0 catabolic parameters.
- Added v3.0 synthetic calibration and frozen-parameter validation-like datasets for software testing; older synthetic artifacts remain historical evidence of previous software versions only.
- Added dedicated regression tests proving that nitrogen exhaustion can stop growth without forcing ethanol production to zero.
- Added `SCIENTIFIC_MODEL_V3.md` with equations, limitations and literature anchors.
- The new non-growth-associated catabolic parameters (`qS_ng_max`, `Ks_cat`, `Kn_cat`, `N_cat_floor`, `N_uncouple_exp`, `Kn_stress`) are **phenomenological reference values and are not calibrated** to a specific strain, medium, vessel or industrial process; v3.0.0 therefore makes no claim of quantitative experimental validation.
- Real-data calibration and the pending real Exp. 3 validation track are explicitly **out of scope for v3.0.0** and are reserved for a later release; no missing experimental observations are fabricated or inferred.

## 2.9.2 — Responsive Scientific GUI Update

- Reworked the Tkinter interface hierarchy with separate brand header and action toolbar.
- Added screen-aware startup geometry and a narrower resizable parameter sidebar.
- Rebuilt the P&ID/operation view using coordinates derived from the actual canvas size.
- Moved critical TRIP indication to a prominent top banner that cannot be clipped below the canvas.
- Added responsive online-value panel with engineering units and bounded layout.
- Replaced the plain alarm text box with a structured, scrollable alarm/event table.
- Improved plot titles, grids, typography and visual consistency across analysis tabs.
- Added mouse-wheel parameter scrolling and keyboard shortcuts for common actions.
- Kept the scientific model, kinetics, numerical solver, audits, validation logic and frozen validation artifacts unchanged.
- Historical validation/calibration reports remain labeled with the software version that produced them (v2.9.1), preserving provenance.

## 2.9.1 — Release Metadata & CI Hotfix

- Fixed invalid GitHub Actions YAML indentation.
- Added workflow YAML validation to the CI job.
- Added `PyYAML` to test dependencies and YAML syntax tests.
- Added complete `authors:` metadata to `CITATION.cff`.
- Added `.zenodo.json` for release metadata.
- Replaced generic authorship placeholders with Renato Dutra Pereira Filho.
- Rewrote `README.md` as a public-facing current-state README.
- Kept scientific model, kinetics, audits and validation logic unchanged.

## 2.9.0 — Frozen-Parameter Independent Validation Update

- Added frozen-parameter independent-validation prediction layer.
- Added CLI `biofermentor-independent-validation`.
- Added calibration-lock loader and SHA-256 tracking.
- Added strict no-refit report flag.
- Added default refusal to evaluate calibration datasets as independent validation.
- Added independent-validation prediction CSV and manifest.
- Added synthetic Exp.3-like validation dataset for software smoke testing.
- Added Valencia-Velásquez et al. Exp.3 pending-data gate documentation.
- Added tests for lock application, no-refit behavior, calibration-set refusal and CLI outputs.
- No real Exp.3 time series are fabricated or included.

## 2.8.0 — Parameter Estimation Update

- Added bounded parameter estimation and calibration locks.

## 2.7.0 — Sensitivity & Practical Identifiability Update

- Added local scaled sensitivity and SVD/correlation diagnostics.

## 2.6.0 — Zero-fit External Validation Update

- Added a priori zero-fit external comparison and qualification gate.

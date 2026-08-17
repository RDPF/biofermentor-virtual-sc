# Scientific status of Biofermentor Virtual SC v3.0.0

## What v3.0.0 is

Biofermentor Virtual SC v3.0.0 is an open, auditable, mechanistic-phenomenological
research and educational simulator for *Saccharomyces cerevisiae* alcoholic
fermentation and process-control studies. It provides a reproducible software
baseline with explicit equations, parameter files, numerical integration, C/N/O₂
integrity audits, sensitivity analysis, practical-identifiability diagnostics,
bounded parameter estimation, and frozen-parameter validation workflows.

The defining scientific change in v3.0.0 is the separation of growth-associated
substrate demand from a bounded non-growth-associated fermentative catabolic
flux. This permits nitrogen limitation to stop biomass growth without forcing
ethanol formation to become zero by construction.

## What v3.0.0 does not claim

The new catabolic parameters (`qS_ng_max`, `Ks_cat`, `Kn_cat`, `N_cat_floor`,
`N_uncouple_exp`, `Kn_stress`) are **phenomenological reference values**. They
are not calibrated to a particular strain, medium composition, fermentor, scale,
or industrial operation.

Therefore v3.0.0 does **not** claim:

- quantitative experimental validation of the complete v3.0 model;
- identification of universal kinetic constants for *S. cerevisiae*;
- digital-twin status for a specific physical fermentor;
- prediction accuracy outside the conditions and assumptions documented in the model;
- completion of the pending real Exp. 3 validation/calibration program.

Synthetic calibration and validation-like datasets in the repository test the
software workflow. They are not experimental evidence.

## Deliberate release boundary

Real-data calibration and the pending real Exp. 3 validation track, including the
Caicedo-Ortega experimental work discussed for future calibration, are reserved
for a later scientific release. This is deliberate: v3.0.0 is intended to be a
stable, citable baseline for the new model structure. Missing experimental points
are not fabricated or inferred to make this release appear complete.

## Recommended wording when citing or describing v3.0.0

A defensible short description is:

> Open mechanistic-phenomenological virtual fermentor with reproducible scientific
> audits and a v3.0 model structure that separates growth-associated and
> non-growth-associated fermentative catabolism. The new catabolic parameters are
> reference values pending experimental calibration.

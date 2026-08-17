# v2.6 Zero-fit protocol — Valencia-Velásquez et al. (2025)

DOI: `10.1007/s00449-025-03222-5`

## Verified experimental design

The publication reports three aerobic batch fermentations. Experiments 1 and 2
form the calibration/training set; Experiment 3 is an independent test batch and
was excluded from fitting in the source study.

Reported operating conditions include:

- 30 °C;
- 0.8 VVM continuous aeration;
- 308 rpm agitation;
- initial pH approximately 5.0, maintained between 4.0 and 5.0;
- working volumes of 300 and 400 mL.

Table 1 reports:

| Set | Sucrose g/L | Glucose g/L | Fructose g/L | Biomass g/L | Urea g/L |
|---|---:|---:|---:|---:|---:|
| Train (mean ± SD, Exp1+Exp2) | 32.7 ± 3.9 | 27.3 ± 3.8 | 27.1 ± 4.1 | 0.5 ± 0.1 | 2.6 ± 0.7 |
| Test (Exp3) | 39.6 | 27.5 | 25.8 | 1.2 | 2.3 |

## Critical mapping limitation

The present Biofermentor core has one fermentable-substrate state `S`, whereas the
paper resolves sucrose, glucose and fructose separately. Therefore the mixed-sugar
time series must **not** be silently collapsed and presented as a one-to-one
validation of substrate kinetics.

The v2.6 baseline should first use directly defensible observables such as biomass
and ethanol, and only use an aggregate-carbon/sugar mapping if that transformation
is separately specified, justified and versioned.

Likewise, model `N` is a generic assimilable-N state while the experiment measures
urea. Any N↔urea comparison must be explicitly qualified.

## Data acquisition gate

No experimental time-series values are included here until they are acquired from
the article's supporting information or reproducibly digitized from Figure 3.

If digitization is required, metadata must record figure/panel, tool, calibration
anchors and protocol. The resulting dataset must retain `data_origin =
digitized_from_figure`.

## Zero-fit rule

No parameter may be estimated from the dataset in v2.6. The baseline uses only
declared prior/default/literature parameters and the experimental initial/operating
conditions. Any later fitting belongs to the parameter-estimation roadmap, not this release.

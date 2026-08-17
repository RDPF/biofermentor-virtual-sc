# Independent Validation Report

- Software version: `2.9.1`
- Analysis: `frozen_parameter_independent_prediction`
- No parameter fitting performed: `True`
- Dataset: `synthetic_exp3_validation_v29`
- Dataset role: `synthetic_demo`
- Data origin: `synthetic`
- Data SHA-256: `52b7b58323164e31552c592493308dd0876a2dfa879acfd729f5636c3d846dd9`
- Metadata SHA-256: `96c54d8427291f0c310cf50ac7bd9806b6d0b1cab9aa02b82d5a4f0c6a1f486f`
- Calibration lock SHA-256: `0fee52a1cc5247ea5515217dde8a77a50a17ed00e3910e4633dbb20d656f247f`
- Calibration dataset: `synthetic_calibration_v28`
- Optimized parameter SHA-256 from lock: `c05b73eaa927c5d2f56cd1fb9f8ae85a5fd7c66d381bfc38d876f7f2c001067d`
- Prediction parameter SHA-256: `c58c3403ee5fca50ba30e359e7f269bc2ccff5f6ecb0d543ac6602d974d7eae9`
- Scientific qualification: **NOT_QUALIFIED**
- Software integrity: **PASS**
- Aggregate mean NRMSE(range): `1.2015560031575625e-14`

## Frozen parameters

| Parameter | Value |
|---|---:|
| `Yps` | 0.44 |
| `Yxs` | 0.16 |
| `mu_max` | 0.34 |

## Metrics by observable

| Variable | n | RMSE | MAE | NRMSE(range) | R² | MBE | Endpoint error |
|---|---:|---:|---:|---:|---:|---:|---:|
| X_g_L | 11 | 3.58725e-14 | 2.67867e-14 | 8.62685e-15 | 1 | 2.67867e-14 | 0 |
| S_g_L | 11 | 2.40985e-13 | 1.89263e-13 | 9.15848e-15 | 1 | -1.35003e-13 | 1.42109e-13 |
| P_g_L | 11 | 6.47222e-14 | 5.33614e-14 | 7.39459e-15 | 1 | 3.39829e-14 | -5.86198e-14 |
| N_g_L | 11 | 4.88003e-15 | 3.44215e-15 | 9.38476e-15 | 1 | -3.42196e-15 | -3.25938e-18 |
| DO_pct | 11 | 1.7677e-12 | 1.0713e-12 | 2.55131e-14 | 1 | 2.25759e-13 | -2.84217e-14 |

## Elemental integrity during prediction

- Carbon: **PASS**, error `2.22208%`
- Nitrogen: **PASS**, error `-0.0332264%`
- Oxygen: **PASS**, error `-0.0121113%`

## Qualification reasons

- dataset role 'synthetic_demo' is not an external-validation role
- data origin 'synthetic' is not external experimental evidence

## Interpretation

Frozen parameters from a prior calibration lock were applied to this dataset. No parameters were estimated from this dataset. If the dataset role/origin are real external evidence, this is an independent validation prediction.

## Scientific limitations

- Independent validation is only as strong as dataset provenance and the prior calibration lock.
- Synthetic datasets can test software behavior but cannot qualify as external experimental validation.
- Good metrics do not prove structural correctness outside the validated experimental domain.

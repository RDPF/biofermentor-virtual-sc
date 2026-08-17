# Parameter Estimation Report

- Software version: `2.9.1`
- Analysis: `bounded_parameter_estimation`
- Dataset: `synthetic_calibration_v28`
- Dataset role: `calibration`
- Data origin: `synthetic`
- Data SHA-256: `07fdd8627b87f36c7543671fa547431a6696ce1be51275ea4fbaeaa5620ec7b6`
- Metadata SHA-256: `2af3877f323da5ddcf1cdcb14541b37c2a703149902a6a03c816ff50c772ea79`
- Initial parameter SHA-256: `94dd0bd808e74c4fbec4eaabfc9f19b6273f9c5a89c599f568aa7a190cd882c5`
- Optimized parameter SHA-256: `c05b73eaa927c5d2f56cd1fb9f8ae85a5fd7c66d381bfc38d876f7f2c001067d`
- Optimizer: `scipy.optimize.least_squares`
- Success: `True`
- Function evaluations: `6`
- Final software integrity: **PASS**

## Objective

- Initial objective: `2.4771689`
- Final objective: `1.7947302e-27`
- Reduction factor: `1.3802458417170407e+27`
- Initial aggregate mean NRMSE(range): `0.2705528091286025`
- Fitted aggregate mean NRMSE(range): `8.040996102450319e-15`

## Estimated parameters

| Parameter | Lower | Initial | Optimized | Upper |
|---|---:|---:|---:|---:|
| `mu_max` | 0.02 | 0.42 | 0.34 | 1.2 |
| `Yxs` | 0.02 | 0.12 | 0.16 | 0.8 |
| `Yps` | 0.05 | 0.49 | 0.44 | 0.7 |

## Metrics after fitting

| Variable | n | RMSE | MAE | NRMSE(range) | R² | MBE |
|---|---:|---:|---:|---:|---:|---:|
| X_g_L | 9 | 3.52793e-14 | 2.64727e-14 | 9.80358e-15 | 1 | 2.64727e-14 |
| S_g_L | 9 | 1.48668e-13 | 1.15266e-13 | 6.53458e-15 | 1 | -9.316e-14 |
| P_g_L | 9 | 5.85085e-14 | 4.2978e-14 | 7.78483e-15 | 1 | 4.06095e-14 |

## Elemental integrity after fitting

- Carbon: **PASS**, error `2.39319%`
- Nitrogen: **PASS**, error `-0.024115%`
- Oxygen: **PASS**, error `-0.0154677%`

## Scientific limitations

- This is calibration, not independent validation.
- Validation datasets must remain untouched and should be evaluated only with frozen optimized parameters.
- Parameter estimates are local and depend on bounds, observable mapping, weights and initial values.
- Passing C/N/O2 integrity audits is necessary but not sufficient for biological validity.

This report is a calibration artifact. It must not be described as external validation.

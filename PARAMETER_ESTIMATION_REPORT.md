# Parameter Estimation Report

- Software version: `3.0.0`
- Analysis: `bounded_parameter_estimation`
- Dataset: `synthetic_calibration_v30`
- Dataset role: `calibration`
- Data origin: `synthetic`
- Data SHA-256: `296e0a38a0bb6c698af78a85019ceefa208d2f062114fb71166b8505bb20e621`
- Metadata SHA-256: `218369338e734eaf9238ee6dfe10d34a553dca522a41c235b815c1cc6454b361`
- Initial parameter SHA-256: `8336f42f3f4018538d168b12db9e8f7453cab9d8967ba865dcbeaf20534f0771`
- Optimized parameter SHA-256: `e5777ecc6d48233a0de54a751fda73f9665df78247035a92e483f285ab94ee23`
- Optimizer: `scipy.optimize.least_squares`
- Success: `True`
- Function evaluations: `7`
- Final software integrity: **PASS**

## Objective

- Initial objective: `1.2988264`
- Final objective: `1.1870115e-28`
- Reduction factor: `1.0941987402057146e+28`
- Initial aggregate mean NRMSE(range): `0.16341108538230878`
- Fitted aggregate mean NRMSE(range): `1.646047632564371e-15`

## Estimated parameters

| Parameter | Lower | Initial | Optimized | Upper |
|---|---:|---:|---:|---:|
| `mu_max` | 0.02 | 0.42 | 0.36 | 1.2 |
| `Yxs` | 0.02 | 0.12 | 0.15 | 0.8 |
| `Yps` | 0.05 | 0.49 | 0.47 | 0.7 |
| `qS_ng_max` | 0 | 0.8 | 0.68 | 3 |

## Metrics after fitting

| Variable | n | RMSE | MAE | NRMSE(range) | R² | MBE |
|---|---:|---:|---:|---:|---:|---:|
| X_g_L | 13 | 5.50825e-15 | 4.85082e-15 | 1.72198e-15 | 1 | -1.22979e-15 |
| S_g_L | 13 | 2.72355e-14 | 2.24094e-14 | 9.03173e-16 | 1 | -1.47574e-14 |
| P_g_L | 13 | 2.42939e-14 | 1.91129e-14 | 2.31299e-15 | 1 | -1.91129e-14 |

## Elemental integrity after fitting

- Carbon: **PASS**, error `1.49583%`
- Nitrogen: **PASS**, error `-0.0703267%`
- Oxygen: **PASS**, error `-0.00583883%`

## Scientific limitations

- This is calibration, not independent validation.
- Validation datasets must remain untouched and should be evaluated only with frozen optimized parameters.
- Parameter estimates are local and depend on bounds, observable mapping, weights and initial values.
- Passing C/N/O2 integrity audits is necessary but not sufficient for biological validity.

This report is a calibration artifact. It must not be described as external validation.

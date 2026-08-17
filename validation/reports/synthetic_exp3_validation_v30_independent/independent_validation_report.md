# Independent Validation Report

- Software version: `3.0.0`
- Analysis: `frozen_parameter_independent_prediction`
- No parameter fitting performed: `True`
- Dataset: `synthetic_exp3_validation_v30`
- Dataset role: `synthetic_demo`
- Data origin: `synthetic`
- Data SHA-256: `468666301fb3bba92e04554ea8bc9d77d173280864f1a4438ca55a253a8b91de`
- Metadata SHA-256: `861fd0c81c32c1c74221566c0e10907c6d730f44c372d4edca785b1e7f9109fa`
- Calibration lock SHA-256: `cf8df43285a3bf87811f3e5bae6f18c5105f18a9f4420415537bc83fa6a08f3b`
- Calibration dataset: `synthetic_calibration_v30`
- Optimized parameter SHA-256 from lock: `e5777ecc6d48233a0de54a751fda73f9665df78247035a92e483f285ab94ee23`
- Prediction parameter SHA-256: `27aeb0b28c3e03e561d9eaedd3ca6c2bc353cd7b2eb1b4fdd190f10005b00bbf`
- Scientific qualification: **NOT_QUALIFIED**
- Software integrity: **PASS**
- Aggregate mean NRMSE(range): `1.4779415619914439e-15`

## Frozen parameters

| Parameter | Value |
|---|---:|
| `Yps` | 0.47 |
| `Yxs` | 0.15 |
| `mu_max` | 0.36 |
| `qS_ng_max` | 0.68 |

## Metrics by observable

| Variable | n | RMSE | MAE | NRMSE(range) | R² | MBE | Endpoint error |
|---|---:|---:|---:|---:|---:|---:|---:|
| X_g_L | 15 | 6.59813e-15 | 4.9886e-15 | 1.50019e-15 | 1 | 4.63333e-15 | 8.88178e-16 |
| S_g_L | 15 | 3.52418e-14 | 2.7948e-14 | 8.9309e-16 | 1 | -1.94215e-14 | -2.13163e-14 |
| P_g_L | 15 | 3.34711e-14 | 1.79782e-14 | 2.41223e-15 | 1 | -1.79782e-14 | -7.4607e-14 |
| N_g_L | 15 | 5.50036e-16 | 3.44125e-16 | 1.00007e-15 | 1 | -3.44125e-16 | -6.16889e-28 |
| DO_pct | 15 | 8.65288e-14 | 6.91595e-14 | 1.58413e-15 | 1 | -2.74743e-14 | -2.84217e-14 |

## Elemental integrity during prediction

- Carbon: **PASS**, error `1.96124%`
- Nitrogen: **PASS**, error `-0.0798511%`
- Oxygen: **PASS**, error `-0.00429482%`

## Qualification reasons

- dataset role 'synthetic_demo' is not an external-validation role
- data origin 'synthetic' is not external experimental evidence

## Interpretation

Frozen parameters from a prior calibration lock were applied to this dataset. No parameters were estimated from this dataset. If the dataset role/origin are real external evidence, this is an independent validation prediction.

## Scientific limitations

- Independent validation is only as strong as dataset provenance and the prior calibration lock.
- Synthetic datasets can test software behavior but cannot qualify as external experimental validation.
- Good metrics do not prove structural correctness outside the validated experimental domain.

# Sensitivity & Practical Identifiability Report

- Software: `3.0.0`
- Analysis: `local_sensitivity_and_practical_identifiability`
- Scope: `nominal_batch_prior_to_parameter_estimation`
- Parameter SHA-256: `a4f0a900ef1c432ef1867f648959e1dc3a2f247a97a7cfb0a0f306281c4ed447`
- Outputs: `X_total, S, P, N, DO_pct`
- Parameters tested: `mu_max, Ks, KiS, Kn, Ko, Pmax, nP, Yxs, Yps, Yxn, ms, qS_ng_max, Ks_cat, Kn_cat, N_cat_floor, N_uncouple_exp, Kcrab, w_crab, kd0, kd_eth`
- Observation times: `401`
- Numerical rank: **19/20**
- Rank deficiency: **1**
- Condition number: `1.76995e+09`

## Sensitivity ranking

| Rank | Parameter | RMS scaled sensitivity | Peak |
|---:|---|---:|---:|
| 1 | `mu_max` | 1.31273 | 30.217 |
| 2 | `w_crab` | 1.20708 | 31.3376 |
| 3 | `Yxs` | 1.00878 | 25.3127 |
| 4 | `Yxn` | 0.369019 | 7.84036 |
| 5 | `Yps` | 0.295298 | 2.43972 |
| 6 | `Kcrab` | 0.212838 | 5.48129 |
| 7 | `Ks` | 0.164511 | 4.86452 |
| 8 | `Kn` | 0.123361 | 3.26713 |
| 9 | `N_uncouple_exp` | 0.0853946 | 2.38741 |
| 10 | `Pmax` | 0.0813567 | 2.23623 |
| 11 | `nP` | 0.079028 | 2.16789 |
| 12 | `Ko` | 0.0716512 | 1.3703 |
| 13 | `KiS` | 0.0600617 | 1.23864 |
| 14 | `qS_ng_max` | 0.0458086 | 1.3111 |
| 15 | `Ks_cat` | 0.0137955 | 0.410527 |
| 16 | `N_cat_floor` | 0.00602815 | 0.177227 |
| 17 | `kd0` | 0.00601406 | 0.162346 |
| 18 | `Kn_cat` | 0.00534832 | 0.156514 |
| 19 | `ms` | 0.00444973 | 0.120953 |
| 20 | `kd_eth` | 1.58508e-06 | 4.70544e-05 |

## Highly correlated parameter pairs

| Parameter 1 | Parameter 2 | cosine similarity |
|---|---|---:|
| `mu_max` | `KiS` | 0.974380 |
| `mu_max` | `Kn` | -0.965241 |
| `mu_max` | `nP` | -0.950273 |
| `mu_max` | `kd0` | -0.960984 |
| `Ks` | `Pmax` | -0.965851 |
| `Ks` | `nP` | 0.964635 |
| `Ks` | `qS_ng_max` | -0.973990 |
| `Ks` | `Ks_cat` | 0.991718 |
| `Ks` | `Kn_cat` | 0.986650 |
| `Ks` | `N_cat_floor` | -0.988705 |
| `Ks` | `N_uncouple_exp` | 0.958444 |
| `Ks` | `kd0` | 0.954800 |
| `Ks` | `kd_eth` | 0.998028 |
| `KiS` | `Ko` | -0.980927 |
| `Kn` | `Pmax` | -0.992522 |
| `Kn` | `nP` | 0.992816 |
| `Kn` | `kd0` | 0.995066 |
| `Pmax` | `nP` | -0.999989 |
| `Pmax` | `qS_ng_max` | 0.961901 |
| `Pmax` | `Kn_cat` | -0.955479 |
| `Pmax` | `N_cat_floor` | 0.952210 |
| `Pmax` | `N_uncouple_exp` | -0.961037 |
| `Pmax` | `kd0` | -0.999109 |
| `Pmax` | `kd_eth` | -0.951874 |
| `nP` | `qS_ng_max` | -0.961111 |
| `nP` | `Kn_cat` | 0.954332 |
| `nP` | `N_cat_floor` | -0.950967 |
| `nP` | `N_uncouple_exp` | 0.960527 |
| `nP` | `kd0` | 0.999292 |
| `nP` | `kd_eth` | 0.950415 |
| `Yxs` | `qS_ng_max` | -0.951889 |
| `Yxs` | `N_uncouple_exp` | 0.970421 |
| `qS_ng_max` | `Ks_cat` | -0.978433 |
| `qS_ng_max` | `Kn_cat` | -0.995782 |
| `qS_ng_max` | `N_cat_floor` | 0.993193 |
| `qS_ng_max` | `N_uncouple_exp` | -0.997448 |
| `qS_ng_max` | `kd0` | -0.953728 |
| `qS_ng_max` | `kd_eth` | -0.965961 |
| `Ks_cat` | `Kn_cat` | 0.993135 |
| `Ks_cat` | `N_cat_floor` | -0.995731 |
| `Ks_cat` | `N_uncouple_exp` | 0.961333 |
| `Ks_cat` | `kd_eth` | 0.993079 |
| `Kn_cat` | `N_cat_floor` | -0.999688 |
| `Kn_cat` | `N_uncouple_exp` | 0.986694 |
| `Kn_cat` | `kd_eth` | 0.982960 |
| `N_cat_floor` | `N_uncouple_exp` | -0.982357 |
| `N_cat_floor` | `kd_eth` | -0.986171 |
| `N_uncouple_exp` | `kd0` | 0.955173 |
| `Kcrab` | `w_crab` | -0.996324 |

## Low-sensitivity parameters

`kd_eth`

## Conservative initial fit subset

`Yps`, `Yxn`, `ms`

## Interpretation

Practical/local screening only; does not establish structural identifiability.

This report is a screening diagnostic. It must not be cited as proof of structural identifiability.

# Sensitivity & Practical Identifiability Report

- Software: `2.7.0`
- Analysis: `local_sensitivity_and_practical_identifiability`
- Scope: `dataset_specific_prior_to_parameter_estimation`
- Parameter SHA-256: `50fc50c2dae3150f7c471a14efc29147371d408e555d3852a9804c89ab9431b6`
- Outputs: `X_total, S, P, N, DO_pct`
- Parameters tested: `mu_max, Yxs, Yps`
- Observation times: `9`
- Numerical rank: **3/3**
- Rank deficiency: **0**
- Condition number: `5.82925`

## Dataset context

- Dataset: `synthetic_demo_v25`
- Role: `synthetic_demo`
- Origin: `synthetic`
- Data SHA-256: `08380da96b972491095d78f1229ce6fc259f8dd1352d233344018f1493e4a5c5`
- Metadata SHA-256: `cab5f35616be47dc0bd08fd378dc70603b9066d8d5be095048a1048318268072`

## Sensitivity ranking

| Rank | Parameter | RMS scaled sensitivity | Peak |
|---:|---|---:|---:|
| 1 | `mu_max` | 1.20144 | 7.62962 |
| 2 | `Yxs` | 0.496941 | 1.20493 |
| 3 | `Yps` | 0.335799 | 0.998234 |

## Highly correlated parameter pairs

None above the configured threshold.

## Low-sensitivity parameters

None.

## Conservative initial fit subset

`mu_max`, `Yxs`, `Yps`

## Interpretation

Practical/local screening only; does not establish structural identifiability.

This report is a screening diagnostic. It must not be cited as proof of structural identifiability.

# v3.0 Scientific Change Verification

This deterministic regression compares the same high-sugar/low-nitrogen batch
scenario (`S0=90 g/L`, `N0=0.45 g/L`, `tf=30 h`) in v2.9.2 and v3.0.0.

| Version | t [h] | S [g/L] | EtOH [g/L] | N [g/L] | mu [1/h] |
|---|---:|---:|---:|---:|---:|
| v2.9.2 | 6 | 59.762 | 11.449 | 1.49e-05 | 0.0001336 |
| v2.9.2 | 20 | 59.006 | 11.700 | 2.03e-42 | 1.821e-41 |
| v2.9.2 | 30 | 58.486 | 11.873 | 8.45e-68 | 7.569e-67 |
| v3.0.0 | 6 | 56.080 | 12.811 | 2.92e-05 | 0.000255 |
| v3.0.0 | 20 | 34.236 | 20.319 | 1.29e-40 | 1.092e-39 |
| v3.0.0 | 30 | 20.686 | 24.800 | 3.24e-64 | 2.661e-63 |

## Structural result

Both versions correctly drive growth toward zero after nitrogen is exhausted.
The difference is carbon catabolism: v2.9.2 leaves only the maintenance-linked
residual, while v3.0.0 retains a bounded non-growth-associated fermentative
flux. Between 6 h and 20 h in the v3.0 case, glucose continues to decrease and
ethanol continues to increase despite essentially zero growth.

This regression is a software/model-structure verification, not experimental
validation. See `SCIENTIFIC_MODEL_V3.md` for the physiological motivation,
parameter status and literature anchors.

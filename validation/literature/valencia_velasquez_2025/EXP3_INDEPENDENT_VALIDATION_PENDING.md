# Exp. 3 independent validation — pending data-ingestion gate

DOI: `10.1007/s00449-025-03222-5`

The v2.9 software can run frozen-parameter prediction on an untouched validation
dataset, but the real Exp. 3 time series from this article have **not** been
ingested here.

Known Table-1 Exp. 3 initial conditions reported in the publication:

| Variable | Value |
|---|---:|
| Sucrose | 39.6 g/L |
| Glucose | 27.5 g/L |
| Fructose | 25.8 g/L |
| Biomass | 1.2 g/L |
| Urea | 2.3 g/L |

The current model has one aggregate substrate state `S`, while the paper resolves
sucrose, glucose and fructose separately. Any future Exp. 3 validation dataset
must explicitly document the mapping or restrict comparison to directly defensible
observables such as biomass, ethanol and possibly DO.

No points were fabricated in v2.9. The real report remains pending until time
series are obtained from supplementary data or reproducibly digitized.

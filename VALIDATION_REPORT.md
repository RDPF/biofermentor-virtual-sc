# Validation Report — v3.0.0

**Automatically generated. Do not edit numerical results manually.**

## Reproducibility identity

- Software version: `3.0.0`
- Default-parameter SHA-256: `879e52ef43c68ec4e631661983636a4c150a07a8657573cecfb94d5f8252fec1`
- Reference integration step: `0.0025` h

Volatile runtime metadata is stored separately in `validation_runtime.json`
when the generator is executed with `--runtime`.

## Reference dynamic mass balances

| Final time | Carbon error | C | Nitrogen error | N | O₂ error | O₂ | Overall |
|---:|---:|---|---:|---|---:|---|---|
| 12 h | +2.961% | PASS | -0.058% | PASS | -0.00908% | PASS | PASS |
| 30 h | +3.472% | PASS | -0.219% | PASS | -0.00220% | PASS | PASS |
| 48 h | +2.626% | PASS | -1.057% | PASS | -0.00146% | PASS | PASS |

Default elemental-balance classification:

- PASS: absolute error ≤ 5%
- WARNING: 5% < absolute error < 10%
- FAIL: absolute error ≥ 10%

## Physiological semantic self-tests

- `zero_substrate_zero_growth`: **PASS**
- `ethanol_limit_zero_growth`: **PASS**
- `temperature_optimum_factor`: **PASS**
- `ph_optimum_factor`: **PASS**
- `low_oxygen_increases_fermentative_fraction`: **PASS**
- `oxygen_solubility_decreases_with_temperature`: **PASS**
- `oxygen_solubility_increases_with_pressure`: **PASS**

## Numerical self-tests

### batch

- `finite`: **PASS**
- `material_states_nonnegative`: **PASS**
- `ph_bounds`: **PASS**
- `temperature_bounds`: **PASS**
- `strict_aux_columns`: **PASS**
- `carbon_audit_finite`: **PASS**
- `nitrogen_audit_finite`: **PASS**
- `oxygen_audit_finite`: **PASS**
- `oxygen_audit_pass`: **PASS**
- `batch_constant_volume`: **PASS**

### fed_exp

- `finite`: **PASS**
- `material_states_nonnegative`: **PASS**
- `ph_bounds`: **PASS**
- `temperature_bounds`: **PASS**
- `strict_aux_columns`: **PASS**
- `carbon_audit_finite`: **PASS**
- `nitrogen_audit_finite`: **PASS**
- `oxygen_audit_finite`: **PASS**
- `oxygen_audit_pass`: **PASS**
- `fedbatch_non_decreasing_volume`: **PASS**

### fed_sstat

- `finite`: **PASS**
- `material_states_nonnegative`: **PASS**
- `ph_bounds`: **PASS**
- `temperature_bounds`: **PASS**
- `strict_aux_columns`: **PASS**
- `carbon_audit_finite`: **PASS**
- `nitrogen_audit_finite`: **PASS**
- `oxygen_audit_finite`: **PASS**
- `oxygen_audit_pass`: **PASS**
- `fedbatch_non_decreasing_volume`: **PASS**

## Interpretation

The carbon and nitrogen audits quantify closure of modeled elemental inventories.
The oxygen audit is a numerical identity check of the liquid-phase O₂ balance:

\[
\frac{d(C_LV)}{dt}=V(OTR-OUR).
\]

It therefore checks consistency among `CL`, `V`, `kLa`, `C*` and `OUR`; it
does **not** independently validate the empirical `kLa` correlation or biological OUR.

Model-integrity validation only; this does not constitute experimental biological validation.

Experimental validation against independent fermentation data remains the next
major scientific maturity milestone.

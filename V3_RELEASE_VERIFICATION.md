# Biofermentor Virtual SC v3.0.0 — Release Verification

Date: 2026-08-16

## Automated verification

- Python syntax compilation: PASS (66 Python files checked)
- Pytest suite: **63/63 PASS** (executed in deterministic batches)
- Scientific self-test: PASS
- Validation report synchronization: PASS
- Practical-identifiability report synchronization: PASS
- GitHub Actions YAML parse: PASS
- GUI smoke test at a 1366×768 virtual display: PASS

## Scientific regression added in v3.0

The release contains tests that verify the new metabolic separation:

1. At `N = 0`, specific growth approaches zero while the bounded
   non-growth-associated catabolic flux can remain positive.
2. Falling nitrogen reduces growth and recruits the nitrogen-limitation
   uncoupling term.
3. In the historical high-sugar/low-nitrogen batch (`S0=90 g/L`, `N0=0.45 g/L`),
   glucose consumption and ethanol formation continue after nitrogen depletion
   instead of collapsing to the maintenance-only residual.
4. The v3.0 reference fed-batch recipe completes without TRIP and passes the
   carbon, nitrogen and oxygen integrity gates used by the release.

## Reproducibility workflow

The v3.0 release includes dedicated synthetic calibration and untouched
synthetic validation datasets. Their purpose is software/workflow verification
only; they are not experimental-validation evidence.

The synthetic calibration smoke test recovers the hidden parameters used to
construct that dataset, and the frozen-parameter synthetic validation test
reproduces the independent synthetic trajectory to numerical precision.

## Scientific status

v3.0.0 is a structural model upgrade, not a claim of experimental validation.
The newly introduced catabolic parameters are phenomenological reference
parameters and must be calibrated and independently validated for a specific
strain, medium, vessel and operating condition before quantitative predictive
claims are made.

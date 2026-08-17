import numpy as np
from .utils import EPS


def _status_from_abs_error(error_pct, p):
    """Classify a mass-balance error using shared PASS/WARNING/FAIL thresholds."""
    e = abs(float(error_pct))
    pass_lim = float(p["mass_balance_pass_abs_error_pct"])
    fail_lim = float(p["mass_balance_fail_abs_error_pct"])
    if fail_lim <= pass_lim:
        raise ValueError("mass_balance_fail_abs_error_pct must exceed pass threshold.")
    if e <= pass_lim:
        return "PASS"
    if e < fail_lim:
        return "WARNING"
    return "FAIL"


def parameter_consistency_audit(p):
    """Static plausibility audit of nominal carbon-yield parameters.

    This is deliberately a parameter audit, not a trajectory mass balance.
    It does not account for the instantaneous metabolic partition phi.
    """
    cin = p["Cfrac_glucose"]
    ferm = (
        p["Yxs"] * p["Cfrac_biomass"]
        + p["Yps"] * p["Cfrac_ethanol"]
        + p["Yco2s_ferm"] * p["Cfrac_co2"]
    ) / max(cin, EPS)
    resp = (
        p["Yxs"] * p["Cfrac_biomass"]
        + p["Yco2s_resp"] * p["Cfrac_co2"]
    ) / max(cin, EPS)
    # v3.0 non-growth fermentative branch has no biomass term.  Reporting
    # this separately prevents the growth-linked plausibility calculation
    # from being misread as the closure of the new catabolic pathway.
    ng_ferm = (
        p["Yps"] * p["Cfrac_ethanol"]
        + p["Yco2s_ferm"] * p["Cfrac_co2"]
    ) / max(cin, EPS)

    warnings = []
    lo, hi = p["carbon_parameter_warn_low"], p["carbon_parameter_warn_high"]
    for label, value in (("fermentativa crescimento-associada", ferm),
                         ("respiratória", resp),
                         ("fermentativa não associada ao crescimento", ng_ferm)):
        if value < lo or value > hi:
            warnings.append(
                f"Recuperação nominal de C {label}={value:.3f} fora de "
                f"[{lo:.2f}, {hi:.2f}]."
            )

    return {
        "carbon_recovery_nominal_ferm": float(ferm),
        "carbon_recovery_nominal_resp": float(resp),
        "carbon_recovery_nominal_ng_ferm": float(ng_ferm),
        "warnings": warnings,
        "scope": "parameter_plausibility_only",
        "status": "WARNING" if warnings else "PASS",
    }


def dynamic_carbon_audit(result, p):
    """Whole-run carbon inventory audit.

    Carbon in:
      initial glucose + ethanol + viable/dead biomass + glucose in feed.

    Carbon accounted:
      final glucose + ethanol + viable/dead biomass + cumulative emitted CO2.

    Closure is *not* forced. Residual carbon exposes unrepresented pools,
    lysis products, other metabolites, or inconsistent phenomenological yields.
    """
    t, Y, U, A = result["t"], result["Y"], result["U"], result["A"]
    V = Y[:, 6]
    Cg, Ce, Cb, Cc = (
        p["Cfrac_glucose"],
        p["Cfrac_ethanol"],
        p["Cfrac_biomass"],
        p["Cfrac_co2"],
    )

    initial_gC = (
        p["S0"] * p["V0"] * Cg
        + p["P0"] * p["V0"] * Ce
        + (p["Xv0"] + p["Xd0"]) * p["V0"] * Cb
    )
    feed_gC = np.trapezoid(U[:, 0] * p["Sfeed"] * Cg, t)

    final_stored_gC = (
        Y[-1, 2] * Y[-1, 6] * Cg
        + Y[-1, 3] * Y[-1, 6] * Ce
        + (Y[-1, 0] + Y[-1, 1]) * Y[-1, 6] * Cb
    )

    # A column 7 = CER [mg CO2/L/h].
    co2_gC_h = (A[:, 7] * V / 1000.0) * Cc
    co2_emitted_gC = np.trapezoid(co2_gC_h, t)

    carbon_in = initial_gC + feed_gC
    accounted = final_stored_gC + co2_emitted_gC
    residual = accounted - carbon_in
    error_pct = 100.0 * residual / max(carbon_in, EPS)
    recovery_pct = 100.0 * accounted / max(carbon_in, EPS)
    status = _status_from_abs_error(error_pct, p)

    warnings = []
    if status != "PASS":
        warnings.append(
            f"Balanço dinâmico de C: {status}; erro={error_pct:.2f}% "
            f"(PASS ≤ ±{p['mass_balance_pass_abs_error_pct']:.1f}%; "
            f"FAIL ≥ ±{p['mass_balance_fail_abs_error_pct']:.1f}%)."
        )

    return {
        "initial_gC": float(initial_gC),
        "feed_gC": float(feed_gC),
        "carbon_in_gC": float(carbon_in),
        "final_stored_gC": float(final_stored_gC),
        "co2_emitted_gC": float(co2_emitted_gC),
        "accounted_gC": float(accounted),
        "residual_gC": float(residual),
        "error_pct": float(error_pct),
        "recovery_pct": float(recovery_pct),
        "status": status,
        "warnings": warnings,
        "interpretation": (
            "Residual is not forced to zero; it exposes unrepresented carbon "
            "pools and/or inconsistency in the phenomenological model."
        ),
    }


def dynamic_nitrogen_audit(result, p):
    """Whole-run nitrogen inventory audit.

    The model consumes nitrogen as qN = mu / Yxn. Therefore 1/Yxn [gN/gX]
    is the internally consistent effective nitrogen fraction of newly formed
    biomass used by this audit.

    Nitrogen in:
      initial dissolved N + effective N in initial viable/dead biomass
      + dissolved N supplied by feed.

    Nitrogen accounted:
      final dissolved N + effective N in final viable/dead biomass.

    Nitrogen released by biomass lysis is not represented as a separate state,
    so lysis can appear as a negative residual. This is intentional and visible.
    """
    t, Y, U = result["t"], result["Y"], result["U"]
    nfrac_biomass = 1.0 / max(p["Yxn"], EPS)

    initial_gN = (
        p["N0"] * p["V0"]
        + (p["Xv0"] + p["Xd0"]) * p["V0"] * nfrac_biomass
    )
    feed_gN = np.trapezoid(U[:, 0] * p["Nfeed"], t)

    final_dissolved_gN = Y[-1, 4] * Y[-1, 6]
    final_biomass_gN = (
        (Y[-1, 0] + Y[-1, 1]) * Y[-1, 6] * nfrac_biomass
    )
    nitrogen_in = initial_gN + feed_gN
    accounted = final_dissolved_gN + final_biomass_gN
    residual = accounted - nitrogen_in
    error_pct = 100.0 * residual / max(nitrogen_in, EPS)
    recovery_pct = 100.0 * accounted / max(nitrogen_in, EPS)
    status = _status_from_abs_error(error_pct, p)

    warnings = []
    if status != "PASS":
        warnings.append(
            f"Balanço dinâmico de N: {status}; erro={error_pct:.2f}% "
            f"(PASS ≤ ±{p['mass_balance_pass_abs_error_pct']:.1f}%; "
            f"FAIL ≥ ±{p['mass_balance_fail_abs_error_pct']:.1f}%)."
        )

    return {
        "effective_biomass_N_fraction_gN_gX": float(nfrac_biomass),
        "initial_gN": float(initial_gN),
        "feed_gN": float(feed_gN),
        "nitrogen_in_gN": float(nitrogen_in),
        "final_dissolved_gN": float(final_dissolved_gN),
        "final_biomass_gN": float(final_biomass_gN),
        "accounted_gN": float(accounted),
        "residual_gN": float(residual),
        "error_pct": float(error_pct),
        "recovery_pct": float(recovery_pct),
        "status": status,
        "warnings": warnings,
        "interpretation": (
            "The audit uses 1/Yxn as the model-consistent biomass N fraction. "
            "Unrepresented nitrogen released by lysis remains visible as residual."
        ),
    }



def dynamic_oxygen_audit(result, p):
    """Dynamic dissolved-oxygen inventory audit in mg O2.

    With:
        dCL/dt = OTR - OUR - D*CL
        dV/dt  = F
        D = F/V

    the liquid inventory M = CL*V satisfies exactly:
        d(CL*V)/dt = V*(OTR - OUR)

    Therefore:
        initial dissolved O2 + cumulative transferred O2
        = final dissolved O2 + cumulative consumed O2

    This audit directly checks numerical consistency among CL, kLa, C*, OUR
    and variable volume. Closure is not forced.
    """
    t, Y, A = result["t"], result["Y"], result["A"]
    V = Y[:, 6]
    CL = Y[:, 5]

    # A columns: 5=kLa [1/h], 6=OUR [mg/L/h], 9=Cstar [mg/L]
    kla = A[:, 5]
    OUR = A[:, 6]
    Cstar = A[:, 9]

    OTR = kla * (Cstar - CL)  # mg/L/h
    transfer_mg_h = OTR * V
    consumption_mg_h = OUR * V

    transferred_mg = np.trapezoid(transfer_mg_h, t)
    consumed_mg = np.trapezoid(consumption_mg_h, t)
    initial_dissolved_mg = CL[0] * V[0]
    final_dissolved_mg = CL[-1] * V[-1]

    lhs = initial_dissolved_mg + transferred_mg
    rhs = final_dissolved_mg + consumed_mg
    residual_mg = rhs - lhs
    error_pct = 100.0 * residual_mg / max(abs(lhs), EPS)
    recovery_pct = 100.0 * rhs / max(abs(lhs), EPS)
    status = _status_from_abs_error(error_pct, p)

    warnings = []
    if status != "PASS":
        warnings.append(
            f"Balanço dinâmico de O2: {status}; erro={error_pct:.3f}% "
            f"(PASS ≤ ±{p['mass_balance_pass_abs_error_pct']:.1f}%; "
            f"FAIL ≥ ±{p['mass_balance_fail_abs_error_pct']:.1f}%)."
        )

    return {
        "initial_dissolved_mgO2": float(initial_dissolved_mg),
        "transferred_mgO2": float(transferred_mg),
        "consumed_mgO2": float(consumed_mg),
        "final_dissolved_mgO2": float(final_dissolved_mg),
        "lhs_mgO2": float(lhs),
        "rhs_mgO2": float(rhs),
        "residual_mgO2": float(residual_mg),
        "error_pct": float(error_pct),
        "recovery_pct": float(recovery_pct),
        "status": status,
        "warnings": warnings,
        "interpretation": (
            "This is a numerical consistency identity for the liquid-phase O2 "
            "balance. It is not an independent experimental validation of kLa or OUR."
        ),
    }


def consolidated_integrity_report(result, p):
    """Return one machine-readable scientific-integrity summary."""
    pa = result["parameter_audit"]
    ca = result["dynamic_carbon_audit"]
    na = result["dynamic_nitrogen_audit"]
    oa = result["dynamic_oxygen_audit"]

    statuses = [pa["status"], ca["status"], na["status"], oa["status"]]
    if "FAIL" in statuses:
        overall = "FAIL"
    elif "WARNING" in statuses:
        overall = "WARNING"
    else:
        overall = "PASS"

    return {
        "overall_status": overall,
        "parameter_status": pa["status"],
        "carbon_status": ca["status"],
        "nitrogen_status": na["status"],
        "oxygen_status": oa["status"],
        "carbon_error_pct": ca["error_pct"],
        "nitrogen_error_pct": na["error_pct"],
        "oxygen_error_pct": oa["error_pct"],
        "warnings": list(result.get("integrity_warnings", [])),
    }

def physiological_self_tests(process, p):
    """Tests of scientific semantics, independent of GUI."""
    y0 = np.array([
        p["Xv0"], p["Xd0"], p["S0"], p["P0"], p["N0"], p["CL0"],
        p["V0"], p["T0"], p["pH0"], p["Foam0"], p["Pr0"]
    ], dtype=float)

    tests = {}

    y = y0.copy()
    y[2] = 0.0
    tests["zero_substrate_zero_growth"] = abs(process.kinetics(y)["mu"]) < 1e-12

    y = y0.copy()
    y[3] = p["Pmax"]
    tests["ethanol_limit_zero_growth"] = abs(process.kinetics(y)["mu"]) < 1e-12

    y = y0.copy()
    y[7] = p["Topt"]
    y[8] = p["pHopt"]
    k = process.kinetics(y)
    tests["temperature_optimum_factor"] = abs(k["fT"] - 1.0) < 1e-12
    tests["ph_optimum_factor"] = abs(k["fpH"] - 1.0) < 1e-12

    y_hi = y0.copy()
    y_hi[5] = 8.0
    y_lo = y0.copy()
    y_lo[5] = 1e-6
    tests["low_oxygen_increases_fermentative_fraction"] = (
        process.kinetics(y_lo)["phi"] >= process.kinetics(y_hi)["phi"]
    )

    c30 = process.oxygen_saturation(30.0, 0.0, 0.2095)
    c25 = process.oxygen_saturation(25.0, 0.0, 0.2095)
    cp = process.oxygen_saturation(30.0, 0.2, 0.2095)
    tests["oxygen_solubility_decreases_with_temperature"] = c25 > c30
    tests["oxygen_solubility_increases_with_pressure"] = cp > c30

    return {name: bool(value) for name, value in tests.items()}


def numerical_self_tests(simulator_cls, defaults_fn):
    """Run representative simulations and verify numerical invariants."""
    cases = [
        ("batch", "Batelada", "Constante"),
        ("fed_exp", "Fed-batch", "Exponencial"),
        ("fed_sstat", "Fed-batch", "S-stat (PID)"),
    ]
    report = {}
    for name, mode, feed in cases:
        p = defaults_fn()
        p["mode"], p["feed_strategy"] = mode, feed
        p["tf"], p["dt"] = 8.0, 0.0025
        r = simulator_cls(p).run()
        Y = r["Y"]
        checks = {
            "finite": bool(np.isfinite(Y).all()),
            "material_states_nonnegative": bool((Y[:, :7] >= -1e-12).all()),
            "ph_bounds": bool(((Y[:, 8] >= 0) & (Y[:, 8] <= 14)).all()),
            "temperature_bounds": bool(((Y[:, 7] >= 0) & (Y[:, 7] <= 80)).all()),
            "strict_aux_columns": r["A"].shape[1] == len(simulator_cls.A_NAMES),
            "carbon_audit_finite": bool(np.isfinite(r["dynamic_carbon_audit"]["error_pct"])),
            "nitrogen_audit_finite": bool(np.isfinite(r["dynamic_nitrogen_audit"]["error_pct"])),
            "oxygen_audit_finite": bool(np.isfinite(r["dynamic_oxygen_audit"]["error_pct"])),
            "oxygen_audit_pass": r["dynamic_oxygen_audit"]["status"] == "PASS",
        }
        if mode == "Batelada":
            checks["batch_constant_volume"] = bool(
                np.max(np.abs(Y[:, 6] - Y[0, 6])) < 1e-9
            )
        else:
            checks["fedbatch_non_decreasing_volume"] = bool(
                (np.diff(Y[:, 6]) >= -1e-12).all()
            )
        report[name] = checks
    return report

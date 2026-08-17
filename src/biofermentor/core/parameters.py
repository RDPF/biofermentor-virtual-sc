def defaults():
    """Return an independent parameter dictionary for the v3.0 scientific reference case."""
    return {
        "mode": "Fed-batch", "tf": 30.0, "dt": 0.0025, "seed": 42,
        "Vmax": 4.75, "Vmin": 0.4,
        "Xv0": 2.0, "Xd0": 0.0, "S0": 25.0, "P0": 0.0, "N0": 0.45,
        "CL0": 6.0, "V0": 2.0, "T0": 30.0, "pH0": 5.0, "Foam0": 0.0, "Pr0": 0.05,

        "feed_strategy": "S-stat (PID)", "feed_start": 3.0,
        "F0": 0.030, "F_slope": 0.003, "feed_mu": 0.12,
        "F_min": 0.0, "F_max": 0.12,
        "Sfeed": 450.0, "Nfeed": 4.0, "Tfeed": 25.0, "pHfeed": 5.0,
        "S_sp": 8.0, "S_kp": 0.012, "S_ki": 0.002, "S_kd": 0.0,

        "mu_max": 0.42, "Ks": 0.50, "KiS": 220.0, "Kn": 0.030, "Ko": 0.50,
        "Pmax": 115.0, "nP": 1.5, "anaer_growth_frac": 0.35,
        "Topt": 30.0, "Twidth": 8.0, "pHopt": 5.0, "pHwidth": 1.3,

        "kd0": 0.003, "kd_eth": 4.0, "death_eth_exp": 3.0,
        "kd_temp": 1.5, "kd_ph": 1.2, "kd_starv": 0.8,
        "T_deadband": 2.0, "pH_deadband": 0.3,
        "kd_max": 0.25, "klysis": 0.005,

        "Yxs": 0.12, "Yps": 0.49, "Yxn": 8.0, "ms": 0.010, "Ks_m": 0.20,
        # v3.0: non-growth-associated catabolic capacity.  These are
        # phenomenological reference values, not strain-universal constants.
        "qS_ng_max": 0.80, "Ks_cat": 1.0,
        "Kn_cat": 0.050, "N_cat_floor": 0.45, "N_uncouple_exp": 1.0,
        "Kn_stress": 0.050,
        "Kcrab": 3.0, "phi_min": 0.15, "w_crab": 0.70,
        "Keth_repress": 0.50, "Kp_cons": 2.0, "qP_cons_max": 0.04,
        "Yo2s": 0.40, "Yo2p": 0.30, "mo2": 0.002,
        "Yco2s_ferm": 0.48, "Yco2s_resp": 1.20,

        "Cfrac_glucose": 72.0/180.0, "Cfrac_ethanol": 24.0/46.0,
        "Cfrac_co2": 12.0/44.0, "Cfrac_biomass": 0.48,
        "carbon_parameter_warn_low": 0.70, "carbon_parameter_warn_high": 1.15,
        "mass_balance_pass_abs_error_pct": 5.0,
        "mass_balance_fail_abs_error_pct": 10.0,
        "RQ_warn_low": 0.4, "RQ_warn_high": 10.0,

        "Cstar_ref": 7.5, "Cstar_Tref": 30.0, "Cstar_temp_coeff": 0.025,
        "kla_ref": 120.0, "rpm_ref": 500.0, "air_ref": 1.0,
        "kla_a": 0.75, "kla_b": 0.40, "kla_v": -0.15, "kla_max": 500.0,
        "rpm_base": 350.0, "rpm_min": 100.0, "rpm_max": 1200.0,
        "gas_base": 0.50, "gas_min": 0.0, "gas_max": 2.0,
        "o2_base": 0.2095, "o2_max": 0.80,

        "DO_strategy": "Sequencial RPM → gás → O₂", "DO_sp": 30.0,
        "DO_kp": 4.0, "DO_ki": 0.25, "DO_kd": 0.0,
        "seq_rpm_gain": 7.0, "seq_gas_thr": 50.0, "seq_gas_gain": 0.015,
        "seq_o2_thr": 40.0, "seq_o2_gain": 0.0035,

        "control_T": True, "T_sp": 30.0,
        "T_kp": 0.60, "T_ki": 0.12, "T_kd": 0.0,
        "Tamb": 25.0, "Qctrl_max": 7.0, "UA_over_rhoCpV": 0.12,
        "deltaH_O2_kJ_mol": 470.0, "rhoCp_kJ_L_K": 4.18,

        "control_pH": True, "pH_sp": 5.0,
        "pH_kp": 2.0, "pH_ki": 0.35, "pH_kd": 0.0,
        "acid_gain": 0.020, "base_gain": 0.020,
        "acid_strength_eq_L": 1.0, "base_strength_eq_L": 1.0,
        "buffer_capacity_eq_L_pH": 0.050,
        "metabolic_acid_eq_per_g_ethanol": 0.0015,

        "foam_control": True, "foam_on": 0.50, "foam_off": 0.20,
        "foam_gen": 0.010, "foam_gas": 0.025, "foam_x": 0.003,
        "foam_decay": 0.20, "antifoam_gain": 1.8,

        "pressure_control": True, "Pr_sp": 0.10, "Pr_kp": 3.0, "Pr_ki": 1.0,
        "Pr_tau": 0.08, "Pr_gas_gain": 0.09, "Pr_vent_gain": 0.12,

        "noise_T": 0.02, "noise_pH": 0.005, "noise_DO": 0.20, "noise_Pr": 0.002,
        "noise_X": 0.01, "noise_S": 0.03, "noise_P": 0.03,
        "tau_Tsens": 0.03, "tau_pHsens": 0.02,
        "tau_DOsens": 0.015, "tau_Prsens": 0.01,

        "T_HH": 35.0, "T_H": 33.0, "T_L": 27.0, "T_LL": 24.0,
        "pH_HH": 6.5, "pH_H": 5.8, "pH_L": 4.2, "pH_LL": 3.5,
        "DO_L": 15.0, "DO_LL": 5.0, "Pr_H": 0.30, "Pr_HH": 0.45,
        "Foam_H": 0.80, "V_HH": 4.90,
        "trip_T_HH": True, "trip_Pr_HH": True, "trip_V_HH": True,
        "recipe_name": "Etanol SC v3 - S-stat com fermentação desacoplada",
    }

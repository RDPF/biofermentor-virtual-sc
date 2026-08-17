import math
import numpy as np
from .utils import clamp, gaussian_factor, EPS


class SCProcess:
    """Phenomenological S. cerevisiae ethanol fermentation model, v3.0.

    v3.0 separates biomass-growth demand from a non-growth-associated
    catabolic glucose flux.  This removes the former structural implication
    that nitrogen exhaustion must force ethanol production to almost zero.

    The model remains deliberately transparent and auditable.  It is not a
    validated digital twin for a specific strain, medium, vessel, or scale.
    The non-growth catabolic parameters are reference values that require
    experimental calibration for quantitative use.
    """

    names = ["Xv", "Xd", "S", "P", "N", "CL", "V", "T", "pH", "Foam", "Pr"]

    def __init__(self, p):
        self.p = p
        self.aux = {}

    def kinetics(self, y):
        p = self.p
        Xv, Xd, S, P, N, CL, V, T, ph, Foam, Pr = y
        S, P, N, CL = max(S, 0.0), max(P, 0.0), max(N, 0.0), max(CL, 0.0)

        # Growth limitation terms.
        fS = S / max(p["Ks"] + S + S*S/max(p["KiS"], EPS), EPS)
        fN = N / max(p["Kn"] + N, EPS)
        fO = CL / max(p["Ko"] + CL, EPS)
        fP = max(0.0, 1.0 - P/max(p["Pmax"], EPS)) ** p["nP"]
        fT = gaussian_factor(T, p["Topt"], p["Twidth"])
        fpH = gaussian_factor(ph, p["pHopt"], p["pHwidth"])
        oxygen_growth = p["anaer_growth_frac"] + (1-p["anaer_growth_frac"])*fO
        mu = p["mu_max"] * fS * fN * fP * fT * fpH * oxygen_growth

        # Stress/death. Carbon starvation remains a mortality modifier.  N
        # stress is reported separately and does not directly cause death in
        # the reference case, avoiding the unjustified N->death shortcut.
        ethanol_stress = (P/max(p["Pmax"], EPS)) ** p["death_eth_exp"]
        temp_stress = max(0.0, abs(T-p["Topt"])-p["T_deadband"]) / max(p["Twidth"], EPS)
        ph_stress = max(0.0, abs(ph-p["pHopt"])-p["pH_deadband"]) / max(p["pHwidth"], EPS)
        carbon_starvation = p["Ks"] / max(p["Ks"]+S, EPS)
        n_stress = p["Kn_stress"] / max(p["Kn_stress"]+N, EPS)
        kd = p["kd0"] * (
            1 + p["kd_eth"]*ethanol_stress + p["kd_temp"]*temp_stress**2
            + p["kd_ph"]*ph_stress**2 + p["kd_starv"]*carbon_starvation
        )
        kd = min(kd, p["kd_max"])

        # Growth-associated glucose demand (Pirt-like growth term).
        qS_growth = mu / max(p["Yxs"], EPS)

        # v3.0 non-growth-associated catabolic pathway.
        # It is progressively recruited when N limits growth, while a bounded
        # fraction of catabolic capacity remains available at N -> 0.
        fS_cat = S / max(p["Ks_cat"] + S, EPS)
        fN_cat = p["N_cat_floor"] + (1.0-p["N_cat_floor"]) * (
            N / max(p["Kn_cat"] + N, EPS)
        )
        n_uncoupling = max(0.0, 1.0-fN) ** p["N_uncouple_exp"]
        qS_ng = (
            p["qS_ng_max"] * fS_cat * fP * fT * fpH
            * fN_cat * n_uncoupling
        )

        # Maintenance is kept separate from product-forming catabolism.
        qS_maint = p["ms"] * S / max(p["Ks_m"]+S, EPS)

        # Respiro-fermentative partition.  Only active metabolic glucose
        # (growth-associated + non-growth catabolic) is product-forming;
        # maintenance is assigned to the respiratory demand term.
        crab = S / max(p["Kcrab"]+S, EPS)
        anaer = 1.0 - fO
        phi = clamp(
            p["phi_min"] + (1-p["phi_min"]) *
            (p["w_crab"]*crab + (1-p["w_crab"])*anaer),
            0.0, 1.0
        )

        qS_active = qS_growth + qS_ng
        qS_ferm = qS_active * phi
        qS_resp = qS_active * (1.0-phi) + qS_maint
        qS = qS_active + qS_maint

        qP = p["Yps"] * qS_ferm
        repression = S / max(p["Keth_repress"]+S, EPS)
        qPcons = (
            p["qP_cons_max"] * P/max(p["Kp_cons"]+P, EPS)
            * fO * (1-repression)
        )
        qN = mu / max(p["Yxn"], EPS)
        qO2 = 1000.0 * (
            p["Yo2s"]*qS_resp + p["mo2"]*fO + p["Yo2p"]*qPcons
        )
        qCO2 = (
            p["Yco2s_ferm"]*qS_ferm +
            p["Yco2s_resp"]*qS_resp
        )
        return dict(
            mu=mu, kd=kd, qS=qS, qP=qP, qPcons=qPcons, qN=qN,
            qO2=qO2, qCO2=qCO2, phi=phi, fO=fO, fS=fS, fN=fN, fP=fP,
            fT=fT, fpH=fpH,
            qS_growth=qS_growth, qS_ng=qS_ng, qS_maint=qS_maint,
            qS_ferm=qS_ferm, qS_resp=qS_resp, fN_cat=fN_cat,
            n_uncoupling=n_uncoupling, n_stress=n_stress,
            carbon_starvation=carbon_starvation,
        )

    def oxygen_saturation(self, T, Pr, o2frac):
        """Return empirical local oxygen saturation C* [mg/L].

        Temperature effect is a transparent local exponential approximation,
        pressure uses absolute pressure ratio, and oxygen enrichment is linear
        in gas-phase O2 mole fraction.
        """
        p = self.p
        pabs = max(1.0 + Pr, 0.2)
        tf = math.exp(-p["Cstar_temp_coeff"] * (T-p["Cstar_Tref"]))
        return p["Cstar_ref"] * tf * (o2frac/0.2095) * pabs

    def rhs(self, t, y, u):
        p = self.p
        Xv, Xd, S, P, N, CL, V, T, ph, Foam, Pr = y
        V = max(V, 1e-6)
        kin = self.kinetics(y)
        F = max(u["feed"], 0.0)
        D = F/V

        gas = max(u["gas"], 0.0)
        o2frac = clamp(u["o2frac"], 0.01, 0.95)
        Cstar = self.oxygen_saturation(T, Pr, o2frac)
        kla = (
            p["kla_ref"] *
            (max(u["rpm"], 1.0)/p["rpm_ref"])**p["kla_a"] *
            (max(gas, 1e-4)/p["air_ref"])**p["kla_b"] *
            (max(V, p["Vmin"])/p["V0"])**p["kla_v"]
        )
        kla = clamp(kla, 0.0, p["kla_max"])

        mu, kd = kin["mu"], kin["kd"]
        dXv = (mu-kd-D)*Xv
        dXd = kd*Xv - p["klysis"]*Xd - D*Xd
        dS = D*(p["Sfeed"]-S) - kin["qS"]*Xv
        dP = -D*P + (kin["qP"]-kin["qPcons"])*Xv
        dN = D*(p["Nfeed"]-N) - kin["qN"]*Xv

        OUR = kin["qO2"]*Xv
        dCL = kla*(Cstar-CL) - OUR - D*CL
        dV = F

        # Oxycalorific heat approximation.
        qmet_kJ_L_h = p["deltaH_O2_kJ_mol"] * OUR / 32000.0
        qmet_K_h = qmet_kJ_L_h / max(p["rhoCp_kJ_L_K"], EPS)
        dT = (
            u["heat"]*p["Qctrl_max"] + qmet_K_h
            + p["UA_over_rhoCpV"]*(p["Tamb"]-T)
            + D*(p["Tfeed"]-T)
        )

        # Semi-mechanistic pH model using buffer capacity.
        acid_met = p["metabolic_acid_eq_per_g_ethanol"]*kin["qP"]*Xv
        acid_dose = p["acid_gain"]*u["acid"]*p["acid_strength_eq_L"]
        base_dose = p["base_gain"]*u["base"]*p["base_strength_eq_L"]
        net_base = base_dose - acid_dose - acid_met
        dpH = net_base/max(p["buffer_capacity_eq_L_pH"], EPS) + D*(p["pHfeed"]-ph)

        foam_src = (
            p["foam_gen"]*max(kin["qCO2"]*Xv, 0.0)
            + p["foam_gas"]*gas + p["foam_x"]*Xv
        )
        dFoam = foam_src - p["foam_decay"]*Foam - p["antifoam_gain"]*u["antifoam"]

        dPr = (
            p["Pr_gas_gain"]*gas - p["Pr_vent_gain"]*u["vent"] - Pr
        ) / max(p["Pr_tau"], EPS)

        CER = 1000.0*kin["qCO2"]*Xv
        RQ = (CER/max(OUR, EPS))*(32.0/44.0)

        self.aux = dict(
            **kin, OUR=OUR, CER=CER, RQ=RQ, kla=kla, Cstar=Cstar,
            D=D, qmet_K_h=qmet_K_h,
        )
        return np.array(
            [dXv,dXd,dS,dP,dN,dCL,dV,dT,dpH,dFoam,dPr],
            dtype=float
        )

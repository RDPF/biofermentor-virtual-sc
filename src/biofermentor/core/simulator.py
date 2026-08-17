import logging
import math
import numpy as np

from .control import PID
from .instrumentation import VirtualSensor, VirtualActuator
from .process import SCProcess
from .recipe import Recipe
from .utils import clamp, EPS
from .validation import (
    parameter_consistency_audit,
    dynamic_carbon_audit,
    dynamic_nitrogen_audit,
    dynamic_oxygen_audit,
    consolidated_integrity_report,
)

LOG = logging.getLogger(__name__)

class SimulationCancelled(RuntimeError):
    """Raised when a caller requests cooperative simulation cancellation."""
    pass


class BiofermentorSimulator:
    U_NAMES = ["feed","acid","base","antifoam","rpm","gas","o2frac","vent","heat","DO_pct"]
    A_NAMES = [
        "mu","kd","qS","qP","phi","kla","OUR","CER","RQ","Cstar","qmet_K_h",
        "qS_growth","qS_ng","qS_maint","qS_ferm","qS_resp",
        "fN_cat","n_uncoupling","n_stress"
    ]

    def __init__(self, p, sensor_faults=None, actuator_faults=None):
        self.p = p
        self.proc = SCProcess(p)
        self.recipe = Recipe(p)
        self.sensor_faults = sensor_faults or {}
        self.actuator_faults = actuator_faults or {}
        seed = int(p.get("seed", 42))

        self.sensors = {
            "T": VirtualSensor("T", p["noise_T"], tau=p["tau_Tsens"], seed=seed+1),
            "pH": VirtualSensor("pH", p["noise_pH"], tau=p["tau_pHsens"], seed=seed+2),
            "DO": VirtualSensor("DO", p["noise_DO"], tau=p["tau_DOsens"], seed=seed+3),
            "Pr": VirtualSensor("Pr", p["noise_Pr"], tau=p["tau_Prsens"], seed=seed+4),
            "Xv": VirtualSensor("Xv", p["noise_X"], tau=0.05, seed=seed+5),
            "S": VirtualSensor("S", p["noise_S"], tau=0.03, seed=seed+6),
            "P": VirtualSensor("P", p["noise_P"], tau=0.03, seed=seed+7),
        }
        for k, v in self.sensor_faults.items():
            if k in self.sensors:
                self.sensors[k].fault = v

        self.acts = {
            "feed": VirtualActuator("Feed", 0, p["F_max"], 0.015),
            "acid": VirtualActuator("Acid", 0, 1, 0.01),
            "base": VirtualActuator("Base", 0, 1, 0.01),
            "antifoam": VirtualActuator("Antifoam", 0, 1, 0.01),
            "rpm": VirtualActuator("Agitator", p["rpm_min"], p["rpm_max"], 0.01),
            "gas": VirtualActuator("Gas MFC", 0, p["gas_max"], 0.01),
            "o2frac": VirtualActuator("O2 mixer", 0.2095, p["o2_max"], 0.01),
            "vent": VirtualActuator("Backpressure valve", 0, 1, 0.005),
            "heat": VirtualActuator("Thermal loop", -1, 1, 0.01),
        }
        for k, v in self.actuator_faults.items():
            if k in self.acts:
                self.acts[k].fault = v

        self.pidT = PID(p["T_kp"], p["T_ki"], p["T_kd"], -1, 1)
        self.pidpH = PID(p["pH_kp"], p["pH_ki"], p["pH_kd"], -1, 1)
        self.pidDO = PID(p["DO_kp"], p["DO_ki"], p["DO_kd"], p["rpm_min"], p["rpm_max"])
        self.pidS = PID(p["S_kp"], p["S_ki"], p["S_kd"], p["F_min"], p["F_max"])
        self.pidPr = PID(p["Pr_kp"], p["Pr_ki"], 0, 0, 1)
        self.foam_latch = False
        self.trip = False
        self.trip_reason = ""
        self.parameter_audit = parameter_consistency_audit(p)

    def measure(self, y, dt, o2frac):
        p = self.p
        Xv, Xd, S, P, N, CL, V, T, ph, Foam, Pr = y
        # DO percent uses current gas oxygen fraction and true thermodynamic state.
        Cstar = self.proc.oxygen_saturation(T, Pr, o2frac)
        DO_true = 100.0*CL/max(Cstar, EPS)
        return {
            "T": self.sensors["T"].measure(T, dt),
            "pH": self.sensors["pH"].measure(ph, dt),
            "DO": self.sensors["DO"].measure(DO_true, dt),
            "Pr": self.sensors["Pr"].measure(Pr, dt),
            "Xv": self.sensors["Xv"].measure(Xv, dt),
            "S": self.sensors["S"].measure(S, dt),
            "P": self.sensors["P"].measure(P, dt),
            "V": V, "Foam": Foam,
        }

    def feed_command(self, t, y, m, phase):
        p = self.p
        if p["mode"] == "Batelada" or not phase.get("feed", False) or t < p["feed_start"]:
            return 0.0
        tau = t-p["feed_start"]
        st = p["feed_strategy"]
        if st == "Constante":
            F = p["F0"]
        elif st == "Rampa linear":
            F = p["F0"] + p["F_slope"]*tau
        elif st == "Exponencial":
            F = p["F0"]*math.exp(p["feed_mu"]*tau)
        elif st == "S-stat (PID)":
            F = self.pidS.step(p["S_sp"], m["S"], p["dt"])
        else:
            raise ValueError(f"Estratégia de alimentação desconhecida: {st}")
        if y[6] >= p["Vmax"]:
            F = 0.0
        return clamp(F, p["F_min"], p["F_max"])

    def commands(self, t, y, m, phase):
        p, dt = self.p, self.p["dt"]
        heat = self.pidT.step(p["T_sp"], m["T"], dt) if p["control_T"] else 0.0

        phu = self.pidpH.step(p["pH_sp"], m["pH"], dt) if p["control_pH"] else 0.0
        acid, base = max(0.0, -phu), max(0.0, phu)

        DOsp = phase.get("DO_sp", p["DO_sp"])
        rpm, gas, o2 = p["rpm_base"], p["gas_base"], p["o2_base"]
        if p["DO_strategy"] == "Fixo":
            pass
        elif p["DO_strategy"] == "PID agitação":
            rpm = self.pidDO.step(DOsp, m["DO"], dt)
        elif p["DO_strategy"] == "Sequencial RPM → gás → O₂":
            e = max(0.0, DOsp-m["DO"])
            effort = max(0.0, p["DO_kp"]*e + p["DO_ki"]*self.pidDO.I)
            self.pidDO.I += e*dt
            rpm = clamp(p["rpm_base"]+p["seq_rpm_gain"]*effort, p["rpm_min"], p["rpm_max"])
            rem = max(0.0, effort-p["seq_gas_thr"])
            gas = clamp(p["gas_base"]+p["seq_gas_gain"]*rem, p["gas_min"], p["gas_max"])
            rem2 = max(0.0, rem-p["seq_o2_thr"])
            o2 = clamp(p["o2_base"]+p["seq_o2_gain"]*rem2, 0.2095, p["o2_max"])
        else:
            raise ValueError(f"Estratégia de DO desconhecida: {p['DO_strategy']}")

        vent = self.pidPr.step(p["Pr_sp"], m["Pr"], dt, reverse=True, bias=0.2) \
            if p["pressure_control"] else 0.4

        if p["foam_control"]:
            if m["Foam"] >= p["foam_on"]:
                self.foam_latch = True
            if m["Foam"] <= p["foam_off"]:
                self.foam_latch = False
        antifoam = 1.0 if self.foam_latch else 0.0

        feed = self.feed_command(t, y, m, phase)

        if self.trip:
            feed = acid = base = antifoam = 0.0
            rpm, gas, o2, heat, vent = p["rpm_min"], 0.0, 0.2095, 0.0, 1.0

        cmd = dict(
            feed=feed, acid=acid, base=base, antifoam=antifoam,
            rpm=rpm, gas=gas, o2frac=o2, vent=vent, heat=heat, DO_pct=m["DO"],
        )
        for k in self.acts:
            cmd[k] = self.acts[k].apply(cmd[k], dt)
        return cmd

    def alarms(self, y, m):
        p = self.p
        a = []
        if m["T"] >= p["T_HH"]: a.append(("HH","Temperatura HH"))
        elif m["T"] >= p["T_H"]: a.append(("H","Temperatura alta"))
        elif m["T"] <= p["T_LL"]: a.append(("LL","Temperatura LL"))
        elif m["T"] <= p["T_L"]: a.append(("L","Temperatura baixa"))

        if m["pH"] >= p["pH_HH"]: a.append(("HH","pH HH"))
        elif m["pH"] >= p["pH_H"]: a.append(("H","pH alto"))
        elif m["pH"] <= p["pH_LL"]: a.append(("LL","pH LL"))
        elif m["pH"] <= p["pH_L"]: a.append(("L","pH baixo"))

        if m["DO"] <= p["DO_LL"]: a.append(("LL","DO muito baixo"))
        elif m["DO"] <= p["DO_L"]: a.append(("L","DO baixo"))
        if m["Pr"] >= p["Pr_HH"]: a.append(("HH","Pressão HH"))
        elif m["Pr"] >= p["Pr_H"]: a.append(("H","Pressão alta"))
        if m["Foam"] >= p["Foam_H"]: a.append(("H","Espuma alta"))
        if m["V"] >= p["V_HH"]: a.append(("HH","Volume HH"))

        if not self.trip:
            if p["trip_T_HH"] and m["T"] >= p["T_HH"]:
                self.trip, self.trip_reason = True, "T HH"
            elif p["trip_Pr_HH"] and m["Pr"] >= p["Pr_HH"]:
                self.trip, self.trip_reason = True, "Pressão HH"
            elif p["trip_V_HH"] and m["V"] >= p["V_HH"]:
                self.trip, self.trip_reason = True, "Volume HH"
        return a

    def rk4(self, t, y, u, dt):
        f = self.proc.rhs
        k1 = f(t, y, u)
        k2 = f(t+dt/2, y+dt*k1/2, u)
        k3 = f(t+dt/2, y+dt*k2/2, u)
        k4 = f(t+dt, y+dt*k3, u)
        z = y + dt*(k1+2*k2+2*k3+k4)/6
        z[:7] = np.maximum(z[:7], 0.0)
        z[7] = clamp(z[7], 0.0, 80.0)
        z[8] = clamp(z[8], 0.0, 14.0)
        z[9] = clamp(z[9], 0.0, 1.5)
        z[10] = clamp(z[10], -0.2, 1.0)
        return z

    def run(self, progress_callback=None, cancel_check=None):
        """Run a deterministic simulation.

        progress_callback(fraction, time_h) is optional and may be called from
        a worker thread. cancel_check() is optional; if it returns True the
        run terminates cooperatively with SimulationCancelled.
        """
        p, dt = self.p, self.p["dt"]
        if dt <= 0 or p["tf"] <= 0:
            raise ValueError("tf e dt devem ser positivos.")
        n = int(p["tf"]/dt)+1
        tv = np.arange(n)*dt
        y = np.array([
            p["Xv0"],p["Xd0"],p["S0"],p["P0"],p["N0"],p["CL0"],
            p["V0"],p["T0"],p["pH0"],p["Foam0"],p["Pr0"]
        ], dtype=float)
        Y = np.zeros((n,11))
        M = np.zeros((n,9))
        U = np.zeros((n,10))
        A = np.zeros((n,len(self.A_NAMES)))
        phases, alarm_rows = [], []
        warnings = list(self.parameter_audit["warnings"])
        rq_warned = False
        last_alarm = set()
        current_o2 = p["o2_base"]
        progress_every = max(1, n // 200)

        for i, t in enumerate(tv):
            if cancel_check is not None and cancel_check():
                raise SimulationCancelled(f"Simulação cancelada em t={t:.3f} h.")
            if progress_callback is not None and (i % progress_every == 0 or i == n-1):
                progress_callback(i / max(n-1, 1), float(t))
            phase = self.recipe.phase_at(t)
            phases.append(phase["name"])
            m = self.measure(y, dt, current_o2)
            al = self.alarms(y, m)
            aset = {msg for _, msg in al}
            for lvl, msg in al:
                if msg not in last_alarm:
                    alarm_rows.append((t,lvl,msg))
            last_alarm = aset

            u = self.commands(t, y, m, phase)
            current_o2 = u["o2frac"]
            self.proc.rhs(t, y, u)
            ax = self.proc.aux.copy()

            Y[i] = y
            M[i] = [m["T"],m["pH"],m["DO"],m["Pr"],m["Xv"],m["S"],m["P"],m["V"],m["Foam"]]
            U[i] = [u[k] for k in self.U_NAMES]
            A[i] = [ax[k] for k in self.A_NAMES]

            if (not rq_warned and ax["OUR"] > 1e-6 and
                (ax["RQ"] < p["RQ_warn_low"] or ax["RQ"] > p["RQ_warn_high"])):
                warnings.append(
                    f"RQ={ax['RQ']:.3f} fora da faixa [{p['RQ_warn_low']:.2f}, "
                    f"{p['RQ_warn_high']:.2f}] em t={t:.3f} h."
                )
                rq_warned = True

            if i < n-1:
                y = self.rk4(t, y, u, dt)

        result = dict(
            t=tv, Y=Y, M=M, U=U, A=A, phases=phases, alarms=alarm_rows,
            trip=self.trip, trip_reason=self.trip_reason,
            parameter_audit=self.parameter_audit,
        )
        result["dynamic_carbon_audit"] = dynamic_carbon_audit(result, p)
        result["dynamic_nitrogen_audit"] = dynamic_nitrogen_audit(result, p)
        result["dynamic_oxygen_audit"] = dynamic_oxygen_audit(result, p)
        warnings.extend(result["dynamic_carbon_audit"]["warnings"])
        warnings.extend(result["dynamic_nitrogen_audit"]["warnings"])
        warnings.extend(result["dynamic_oxygen_audit"]["warnings"])
        result["integrity_warnings"] = warnings
        result["integrity_report"] = consolidated_integrity_report(result, p)
        if progress_callback is not None:
            progress_callback(1.0, float(tv[-1]))
        return result

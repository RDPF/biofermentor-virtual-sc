from .utils import clamp, EPS

class PID:
    """Discrete PID with conditional anti-windup and derivative on measurement."""
    def __init__(self, kp=1.0, ki=0.0, kd=0.0, umin=0.0, umax=1.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.umin, self.umax = umin, umax
        self.reset()

    def reset(self):
        self.I = 0.0
        self.pv_prev = None

    def step(self, sp, pv, dt, reverse=False, bias=0.0):
        e = (pv - sp) if reverse else (sp - pv)
        dpv = 0.0 if self.pv_prev is None else (pv - self.pv_prev) / max(dt, EPS)
        dterm = self.kd * (dpv if reverse else -dpv)
        Itrial = self.I + e * dt
        raw = bias + self.kp * e + self.ki * Itrial + dterm
        u = clamp(raw, self.umin, self.umax)
        if abs(u - raw) < 1e-12 or (u >= self.umax and e < 0) or (u <= self.umin and e > 0):
            self.I = Itrial
        self.pv_prev = pv
        return u

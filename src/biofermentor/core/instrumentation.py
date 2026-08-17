import random
from .utils import first_order, clamp

class VirtualSensor:
    def __init__(self, name, noise=0.0, bias=0.0, tau=0.0, seed=1):
        self.name, self.noise, self.bias, self.tau = name, noise, bias, tau
        self.rng = random.Random(seed)
        self.value = None
        self.fault = "Normal"
        self.locked = None

    def measure(self, true, dt):
        if self.value is None:
            self.value = true
        self.value = first_order(self.value, true, self.tau, dt)
        n, b = self.noise, self.bias
        if self.fault == "Bias+":
            b += 5*n if n > 0 else 0.5
        elif self.fault == "Bias-":
            b -= 5*n if n > 0 else 0.5
        elif self.fault == "Ruído alto":
            n *= 8
        elif self.fault == "Zero":
            return 0.0
        elif self.fault == "Travado":
            if self.locked is None:
                self.locked = self.value + b
            return self.locked
        return self.value + b + self.rng.gauss(0.0, n)

class VirtualActuator:
    def __init__(self, name, umin, umax, tau=0.02):
        self.name, self.umin, self.umax, self.tau = name, umin, umax, tau
        self.value = umin
        self.fault = "Normal"
        self.locked = None

    def apply(self, cmd, dt):
        cmd = clamp(cmd, self.umin, self.umax)
        if self.fault == "0%":
            cmd = self.umin
        elif self.fault == "50%":
            cmd = (self.umin + self.umax) / 2
        elif self.fault == "100%":
            cmd = self.umax
        elif self.fault == "Travado":
            if self.locked is None:
                self.locked = self.value
            cmd = self.locked
        self.value = first_order(self.value, cmd, self.tau, dt)
        return self.value

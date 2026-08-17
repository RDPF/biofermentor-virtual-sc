import math
EPS = 1e-12

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def gaussian_factor(x, opt, width):
    width = max(abs(width), 1e-9)
    return math.exp(-((x - opt) / width) ** 2)

def first_order(prev, target, tau, dt):
    if tau <= 0:
        return target
    a = 1.0 - math.exp(-dt / max(tau, EPS))
    return prev + a * (target - prev)

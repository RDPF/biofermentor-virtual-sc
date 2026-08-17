from biofermentor.core.control import PID

def test_derivative_on_measurement_no_setpoint_kick():
    pid = PID(kp=0.0, ki=0.0, kd=2.0, umin=-100, umax=100)
    u1 = pid.step(1.0, 0.0, 1.0)
    u2 = pid.step(10.0, 0.0, 1.0)
    assert abs(u1) < 1e-12
    assert abs(u2) < 1e-12

def test_derivative_responds_to_measurement_change():
    pid = PID(kp=0.0, ki=0.0, kd=2.0, umin=-100, umax=100)
    pid.step(1.0, 0.0, 1.0)
    u = pid.step(1.0, 1.0, 1.0)
    assert u < 0

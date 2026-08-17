from biofermentor.core import defaults, BiofermentorSimulator

p = defaults()
p["mode"] = "Fed-batch"
p["tf"] = 12.0
p["dt"] = 0.01

r = BiofermentorSimulator(p).run()
print("Etanol final [g/L]:", r["Y"][-1, 3])
print("Carbon recovery [%]:", r["dynamic_carbon_audit"]["recovery_pct"])

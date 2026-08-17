"""Headless command-line entry point. Does not import GUI modules."""
import argparse
import json
import logging
from pathlib import Path

from .core import defaults, BiofermentorSimulator
from .core.process import SCProcess
from .core.validation import physiological_self_tests, numerical_self_tests

def self_test():
    p = defaults()
    phys = physiological_self_tests(SCProcess(p), p)
    numerical = numerical_self_tests(BiofermentorSimulator, defaults)
    ok = all(phys.values()) and all(all(c.values()) for c in numerical.values())
    report = {"physiological": phys, "numerical": numerical, "pass": ok}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if ok else 1

def run_case(args):
    p = defaults()
    p["mode"] = args.mode
    p["tf"] = args.tf
    p["dt"] = args.dt
    r = BiofermentorSimulator(p).run()
    summary = {
        "Xv_final_g_L": float(r["Y"][-1,0]),
        "S_final_g_L": float(r["Y"][-1,2]),
        "P_final_g_L": float(r["Y"][-1,3]),
        "V_final_L": float(r["Y"][-1,6]),
        "dynamic_carbon": r["dynamic_carbon_audit"],
        "dynamic_nitrogen": r["dynamic_nitrogen_audit"],
        "dynamic_oxygen": r["dynamic_oxygen_audit"],
        "integrity_report": r["integrity_report"],
        "warnings": r["integrity_warnings"],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0

def main(argv=None):
    ap = argparse.ArgumentParser(prog="biofermentor")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["Batelada","Fed-batch"], default="Fed-batch")
    ap.add_argument("--tf", type=float, default=12.0)
    ap.add_argument("--dt", type=float, default=0.01)
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    if args.self_test:
        return self_test()
    return run_case(args)

if __name__ == "__main__":
    raise SystemExit(main())

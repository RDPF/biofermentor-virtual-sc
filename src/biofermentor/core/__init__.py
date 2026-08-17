"""Headless scientific core. This package never imports Tkinter or Matplotlib."""
from .parameters import defaults
from .process import SCProcess
from .simulator import BiofermentorSimulator, SimulationCancelled
from .validation import (
    parameter_consistency_audit,
    dynamic_carbon_audit,
    dynamic_nitrogen_audit,
    dynamic_oxygen_audit,
    consolidated_integrity_report,
    physiological_self_tests,
    numerical_self_tests,
)
__all__ = [
    "defaults", "SCProcess", "BiofermentorSimulator", "SimulationCancelled",
    "parameter_consistency_audit", "dynamic_carbon_audit",
    "dynamic_nitrogen_audit", "dynamic_oxygen_audit", "consolidated_integrity_report",
    "physiological_self_tests", "numerical_self_tests",
]

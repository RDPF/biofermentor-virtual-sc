"""Convenience self-test launcher for the source checkout."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from biofermentor.cli import self_test


if __name__ == "__main__":
    raise SystemExit(self_test())

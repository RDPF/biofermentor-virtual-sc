"""Convenience launcher for the source checkout.

This file also works before an editable/package installation by adding the local
``src`` directory to ``sys.path``. Installed users can still use the
``biofermentor-gui`` console entry point defined in ``pyproject.toml``.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from biofermentor.gui.app import main


if __name__ == "__main__":
    main()

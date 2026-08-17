import sys

def test_core_does_not_import_gui_dependencies():
    import biofermentor.core  # noqa
    forbidden = {"tkinter", "matplotlib", "matplotlib.pyplot"}
    loaded = forbidden.intersection(sys.modules)
    assert not loaded, f"GUI dependencies leaked into core import: {loaded}"

from pathlib import Path

import yaml


def test_citation_cff_has_required_public_release_fields(project_root):
    cff = yaml.safe_load((project_root / "CITATION.cff").read_text(encoding="utf-8"))
    assert cff["version"] == "3.0.0"
    assert cff["authors"]
    assert cff["authors"][0]["family-names"] == "Pereira Filho"
    assert cff["license"] == "BSD-3-Clause"


def test_zenodo_json_has_creator_and_license(project_root):
    import json
    z = json.loads((project_root / ".zenodo.json").read_text(encoding="utf-8"))
    assert z["version"] == "3.0.0"
    assert z["creators"][0]["name"] == "Pereira Filho, Renato Dutra"
    assert z["license"] == "BSD-3-Clause"

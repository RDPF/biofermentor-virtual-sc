from pathlib import Path

import yaml


def test_github_actions_workflow_yaml_is_valid(project_root):
    path = project_root / ".github" / "workflows" / "tests.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["name"] == "scientific-tests"
    steps = data["jobs"]["scientific-core"]["steps"]
    names = [s.get("name") for s in steps if isinstance(s, dict)]
    assert "Verify parameter estimation smoke test" in names
    assert "Verify independent validation smoke test" in names
    assert "Validate workflow YAML" in names

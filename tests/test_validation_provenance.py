from biofermentor.validation_data import load_dataset_directory


def test_dataset_provenance_hashes_are_stable(project_root):
    d = project_root / "validation" / "datasets" / "synthetic_demo"
    a = load_dataset_directory(d)
    b = load_dataset_directory(d)
    assert a.data_sha256 == b.data_sha256
    assert a.metadata_sha256 == b.metadata_sha256
    assert len(a.data_sha256) == 64
    assert len(a.metadata_sha256) == 64

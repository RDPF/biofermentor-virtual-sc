import csv
import json
from pathlib import Path
import numpy as np

from .dataset import ExperimentalDataset, ValidationDatasetError
from .schema import CANONICAL_COLUMNS
from .provenance import sha256_file


def _float_or_nan(value):
    s = str(value).strip()
    if s == "":
        return float("nan")
    return float(s.replace(",", "."))


def load_dataset_directory(directory):
    directory = Path(directory)
    metadata_path = directory / "metadata.json"
    data_path = directory / "data.csv"

    if not metadata_path.exists():
        raise ValidationDatasetError(f"Missing {metadata_path}")
    if not data_path.exists():
        raise ValidationDatasetError(f"Missing {data_path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    with data_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValidationDatasetError("CSV has no header")
        unknown = sorted(set(reader.fieldnames) - set(CANONICAL_COLUMNS))
        if unknown:
            raise ValidationDatasetError(
                f"Unknown canonical CSV columns: {unknown}"
            )
        rows = list(reader)

    if not rows:
        raise ValidationDatasetError("data.csv is empty")

    data = {}
    for col in reader.fieldnames:
        data[col] = np.array([_float_or_nan(r[col]) for r in rows], dtype=float)

    dataset = ExperimentalDataset(
        directory=directory,
        metadata=metadata,
        columns=tuple(reader.fieldnames),
        data=data,
        data_sha256=sha256_file(data_path),
    )
    return dataset.validate()

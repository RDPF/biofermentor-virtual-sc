from dataclasses import dataclass
from pathlib import Path
import numpy as np

from .schema import (
    SCHEMA_VERSION,
    CANONICAL_COLUMNS,
    OBSERVABLE_COLUMNS,
    ALLOWED_DATASET_ROLES,
    ALLOWED_DATA_ORIGINS,
    REQUIRED_METADATA_FIELDS,
    REQUIRED_EXPERIMENT_FIELDS,
    REQUIRED_INITIAL_CONDITIONS,
)
from .provenance import canonical_json_sha256


class ValidationDatasetError(ValueError):
    pass


@dataclass(frozen=True)
class ExperimentalDataset:
    directory: Path
    metadata: dict
    columns: tuple
    data: dict
    data_sha256: str

    @property
    def dataset_id(self):
        return self.metadata["dataset_id"]

    @property
    def role(self):
        return self.metadata["role"]

    @property
    def time_h(self):
        return self.data["time_h"]

    @property
    def observable_columns(self):
        return tuple(c for c in OBSERVABLE_COLUMNS if c in self.data)

    @property
    def metadata_sha256(self):
        return canonical_json_sha256(self.metadata)

    def validate(self):
        md = self.metadata
        missing = sorted(REQUIRED_METADATA_FIELDS - set(md))
        if missing:
            raise ValidationDatasetError(f"Missing metadata fields: {missing}")

        if md.get("schema_version") != SCHEMA_VERSION:
            raise ValidationDatasetError(
                f"schema_version must be {SCHEMA_VERSION!r}; "
                f"got {md.get('schema_version')!r}"
            )

        if md["role"] not in ALLOWED_DATASET_ROLES:
            raise ValidationDatasetError(f"Invalid dataset role: {md['role']}")
        if md["data_origin"] not in ALLOWED_DATA_ORIGINS:
            raise ValidationDatasetError(f"Invalid data_origin: {md['data_origin']}")

        exp = md["experiment"]
        missing_exp = sorted(REQUIRED_EXPERIMENT_FIELDS - set(exp))
        if missing_exp:
            raise ValidationDatasetError(f"Missing experiment fields: {missing_exp}")

        ic = exp["initial_conditions"]
        missing_ic = sorted(REQUIRED_INITIAL_CONDITIONS - set(ic))
        if missing_ic:
            raise ValidationDatasetError(
                f"Missing initial-condition fields: {missing_ic}"
            )

        if "time_h" not in self.data:
            raise ValidationDatasetError("time_h is required")
        if not self.observable_columns:
            raise ValidationDatasetError(
                "At least one experimental observable must be present"
            )

        t = np.asarray(self.time_h, dtype=float)
        if len(t) < 2:
            raise ValidationDatasetError("At least two time points are required")
        if not np.all(np.isfinite(t)):
            raise ValidationDatasetError("time_h contains non-finite values")
        if np.any(np.diff(t) <= 0):
            raise ValidationDatasetError("time_h must be strictly increasing")
        if t[0] < 0:
            raise ValidationDatasetError("time_h cannot be negative")

        for col in self.observable_columns:
            x = np.asarray(self.data[col], dtype=float)
            if len(x) != len(t):
                raise ValidationDatasetError(
                    f"{col} length differs from time_h length"
                )
            # NaN is allowed to represent an unmeasured point; infinity is not.
            if np.any(np.isinf(x)):
                raise ValidationDatasetError(f"{col} contains infinity")
            if col != "DO_pct":
                finite = x[np.isfinite(x)]
                if finite.size and np.any(finite < 0):
                    raise ValidationDatasetError(
                        f"{col} contains negative physical concentrations"
                    )

        mapping = md["model_mapping"]
        for obs in self.observable_columns:
            if obs not in mapping:
                raise ValidationDatasetError(
                    f"Missing model_mapping entry for {obs}"
                )

        if md["data_origin"] == "digitized_from_figure":
            digit = md.get("digitization")
            if not digit:
                raise ValidationDatasetError(
                    "digitization metadata required for digitized data"
                )
            for field in ("figure", "tool", "protocol"):
                if field not in digit:
                    raise ValidationDatasetError(
                        f"digitization.{field} is required"
                    )

        return self

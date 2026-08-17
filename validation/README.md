# External Validation Workspace

This directory contains datasets and derived validation artifacts.

## Rules

1. Raw/source-derived data must never be silently edited.
2. Every dataset directory contains `metadata.json` + canonical `data.csv`.
3. Dataset role is explicit: calibration, validation, external_replication, or synthetic_demo.
4. Data origin is explicit: original_open_data, supplementary_information,
   digitized_from_figure, or synthetic.
5. Digitized data require figure/tool/protocol metadata.
6. Calibration datasets and untouched validation datasets must remain distinct.
7. The v2.5 pipeline performs **zero-fit comparison only**; it does not estimate parameters.

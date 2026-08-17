"""Scientific qualification gates for external-validation claims."""

EXTERNAL_ORIGINS = {
    "original_open_data",
    "supplementary_information",
    "digitized_from_figure",
}

def qualification(dataset, report=None):
    reasons = []
    if dataset.role not in {"validation", "external_replication"}:
        reasons.append(
            f"dataset role {dataset.role!r} is not an external-validation role"
        )
    if dataset.metadata["data_origin"] not in EXTERNAL_ORIGINS:
        reasons.append(
            f"data origin {dataset.metadata['data_origin']!r} is not external experimental evidence"
        )
    source = dataset.metadata.get("source", {})
    if not (source.get("doi") or source.get("url") or source.get("citation")):
        reasons.append("source provenance is missing")
    if dataset.metadata["data_origin"] == "digitized_from_figure":
        digit = dataset.metadata.get("digitization", {})
        if not digit.get("figure") or not digit.get("tool") or not digit.get("protocol"):
            reasons.append("digitization provenance is incomplete")

    if report is not None:
        integ = report.get("software_integrity", {})
        if integ.get("overall_status") == "FAIL":
            reasons.append("software integrity report is FAIL")

    return {
        "qualified_external_validation": not reasons,
        "status": "QUALIFIED" if not reasons else "NOT_QUALIFIED",
        "reasons": reasons,
    }

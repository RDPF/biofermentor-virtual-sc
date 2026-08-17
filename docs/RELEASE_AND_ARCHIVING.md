# GitHub and Zenodo release procedure for v3.0.0

This document is an operational checklist for publishing the already-scoped
v3.0.0 release. It must not be used as an excuse to add new scientific work to
the release.

## 1. Before pushing to GitHub

- Confirm `pyproject.toml`, `CITATION.cff` and `.zenodo.json` all report version `3.0.0`.
- Confirm the catabolic-parameter caveat is present in `README.md`, `CHANGELOG.md`,
  `CITATION.cff` and `.zenodo.json`.
- Confirm real-data calibration / real Exp. 3 work remains explicitly pending.
- Run the scientific self-test and complete pytest suite.
- Verify `RELEASE_MANIFEST.json`.
- Confirm no secrets, credentials, local paths or private experimental files are tracked.

## 2. GitHub repository

Create the repository and push this directory as the repository root. Keep
`CITATION.cff` and `.zenodo.json` at the root. The default branch should contain
the exact content intended for the release before tagging.

Recommended first public tag:

```text
v3.0.0
```

Use `GITHUB_RELEASE_NOTES_v3.0.0.md` as the basis for the GitHub Release text.

## 3. Zenodo integration

Connect the GitHub account to Zenodo, enable this repository in Zenodo's GitHub
integration, and only then create/publish the GitHub `v3.0.0` release. Zenodo can
archive enabled GitHub releases and assign a version-specific DOI.

This repository intentionally contains both metadata files:

- `.zenodo.json`: authoritative metadata for Zenodo's GitHub release ingestion;
- `CITATION.cff`: citation metadata for GitHub's “Cite this repository” interface.

When both are present, Zenodo uses `.zenodo.json` for GitHub release archiving,
so its description must contain the scientific limitations that users should see
without opening the repository.

## 4. After the DOI is assigned

- Record the version-specific DOI in the GitHub Release description.
- Add a DOI badge/link to the default branch README if desired.
- Update `CITATION.cff` on the default branch with the real DOI if desired for
  GitHub citation convenience.
- Do **not** delete/recreate or silently retag `v3.0.0` merely to insert the DOI
  into the already archived source snapshot. Preserve the released object.

## 5. Scope that remains for a later DOI

Do not add real-data calibration, pending real Exp. 3 observations, or a new
parameter-identification claim to this release after publication. Those are new
scientific results and should be released under a later semantic version with
their own Zenodo version DOI.

## Official references

- Zenodo GitHub integration: https://help.zenodo.org/docs/github/
- Zenodo `.zenodo.json`: https://help.zenodo.org/docs/github/describe-software/zenodo-json/
- Zenodo GitHub release archiving: https://help.zenodo.org/docs/github/archive-software/github-upload/
- GitHub `CITATION.cff`: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files

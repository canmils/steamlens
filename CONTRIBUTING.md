# Contributing to SteamLens

Read README.md for supported installation, public-data limits, privacy and costs.

## Report a problem or suggest a change

Use https://github.com/canmils/steamlens/issues. Include OS/Python version, commit
(`git rev-parse HEAD`), App IDs, exact steps, sanitized error and expected/actual behavior.
Feature requests should identify the user problem, evidence and an example.
Do not share credentials, private commercial data or unsupported performance claims.

## Submit a change

1. Fork this repo, clone your fork and add upstream:
   `git remote add upstream https://github.com/canmils/steamlens.git`.
2. Create a focused branch: `git switch -c improve-checklist`.
3. Install with the README's virtual-environment commands. Make one focused change.
4. Run `python -m pytest -q` using that environment. Add meaningful fixtures/tests for behavior changes.
   Docker changes also need the Compose build/health checks. Live Steam/paid AI checks are separate;
   record which checks were actually run and which were unavailable.
5. If deterministic output changes intentionally, regenerate `examples/fictional-audit.json`
   from the fixture using `audit`, `store_checklist` and `positioning`; review the differences.
6. Review `git diff` and `git status`, commit intended files, push your branch and open a PR
   to `main`. Describe the user problem, resulting behavior, validation and remaining limits.

Use fictional or explicitly licensed fixtures; preserve attribution and dependency notices.
Data-source changes need provenance and usage-policy review. Do not add unverifiable sales,
wishlist or conversion estimates. A source quote does not validate an AI interpretation.
Open an issue before substantial architecture changes. Maintainers review before merging.

# SteamLens v0.5.1 — experimental beta release gate

**Release scope:** stability, honesty, documentation and testing only. No new product features before developer feedback.

## Maintainer checks (must pass before release)

- [ ] GitHub Actions test workflow is green for Python 3.10 and 3.12 on this PR.
- [ ] Fresh virtual environment: install `requirements.txt`, run `python -m pytest -q`, start Streamlit.
- [ ] Run a normal released game with three comparison games: `1145360` vs `1145350, 588650, 2071280`.
- [ ] Run a game with incomplete or unavailable metadata; confirm the UI fails gracefully and does not invent missing values.
- [ ] Run without `OPENAI_API_KEY`: checklist and comparison still work; AI is skipped.
- [ ] Run with a valid personal API key: 2–3 AI hypotheses are displayed; test JSON export includes the AI review.
- [ ] Run with an invalid API key: clear error; checklist and comparison remain available.
- [ ] Check README install steps on a clean machine, Docker build if available, and public links.
- [ ] Check no secrets, credentials or personal data have been committed or included in screenshots.
- [ ] Confirm the public Steam endpoint usage and any relevant usage constraints for the intended release model.
- [ ] Confirm UI and README consistently say *experimental*, avoid conversion/sales claims and identify AI costs.
- [ ] Confirm screenshots and demo materials are available and accurate.

## Release steps

1. Merge this PR only after checks pass.
2. Tag the tested main-branch commit `v0.5.1` and publish a GitHub pre-release titled **SteamLens v0.5.1 — Experimental Beta**.
3. Include setup instructions, limitations and known issues in the release notes.
4. Share with 5–10 indie developers. Ask for an App ID, what they learned, what they would change, and whether they would use it again. Direct bug reports to GitHub Issues.
5. Freeze new features until feedback is reviewed. Fix only critical bugs/security issues in the interim.

## Go/no-go

**Go** only if all required checks pass and there are no known credential leaks or blocking failures.

**No-go** if installation is broken, API keys leak, AI errors prevent free analysis, or reported output makes unsupported performance claims.

**Feedback decision after first 5–10 users:** continue only if at least two developers report a specific, previously unnoticed, actionable finding. Otherwise reassess the core value proposition.

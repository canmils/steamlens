# Contributing to SteamLens

Thanks for helping improve SteamLens. Developers, marketers, testers, documentation writers and first-time open-source contributors are welcome.

## No coding required: share feedback

Run SteamLens using the [README instructions](README.md). Use the [GitHub Issues form](https://github.com/canmils/steamlens/issues/new/choose) to:
- **Report a bug:** include public Steam App IDs, steps to reproduce, expected vs actual results, OS, and a sanitized error message.
- **Share beta feedback:** tell us whether you discovered a *new, actionable* insight, what you would change, and whether you would use the tool again.
- **Suggest an improvement:** explain the user problem and what is currently missing.

You need a free GitHub account to submit an Issue or PR. You do not need to know Python. Please search [existing Issues](https://github.com/canmils/steamlens/issues) first to avoid duplicates.

**Never share API keys, passwords, private Steamworks analytics, personal information, or confidential game data.** Public App IDs and store-page URLs are fine.

## Make a code or documentation contribution

1. Open an Issue before large changes, particularly new features.
2. Fork [canmils/steamlens](https://github.com/canmils/steamlens), clone your fork and create a branch from `main`.
3. Install Python 3.10+ dependencies: `python -m pip install -r requirements.txt`.
4. Make a focused change. Add or update tests when changing behavior.
5. Run `python -m pytest -q` and `python -m compileall -q app`.
6. Commit changes to your branch and push to your fork.
7. Open a pull request targeting `canmils/steamlens:main`, link the Issue, explain the change and include sanitized screenshots for UI changes.
8. Respond to review comments. Maintainers may request changes or decline a PR; opening a PR does not guarantee acceptance.

GitHub Actions runs the test suite on PRs. Tests must not need live OpenAI credentials; mock external calls in unit tests. Document the source and usage terms for any new external data integration.

## Current project policy

**Experimental beta / feature freeze:** until feedback from 5–10 real users is reviewed, prioritize bugs, security, reliability, documentation, accessibility, and tests. Propose larger features in an Issue, but do not start major development expecting immediate merge.

Avoid undocumented scraping, secret leaks, fabricated marketing metrics, and AI interpretations presented as proven facts. SteamLens is local-first and must remain useful without an OpenAI key.

## Maintainer release process

See [docs/BETA_RELEASE.md](docs/BETA_RELEASE.md). Only maintainers merge PRs and create GitHub releases after verification.

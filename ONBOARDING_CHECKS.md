# Verification record

## 15 October 2026

- Fresh Python 3.12 virtual environment installed from requirements on Linux.
- **34 offline tests passed**: parsing, deterministic checks, positioning, quote validation,
  provider request structure and Streamlit onboarding/error/export paths.
- Free UI test verifies target rendering, comparison table, JSON download and no AI call.
- Failed competitor leaves target report available; failed target shows an error without export.
- Successful mocked AI review is included in exported JSON; test key is not exported.
- Failed mocked AI review leaves free checklist and positioning export available.
- Fictional example JSON is recomputed and checked against the implementation.
- Two-fragment stitched quotes are rejected; typography/case/spacing normalization remains supported.
- Live `scripts/check_live.py --live` succeeded for Hades (1145360), Hades II (1145350),
  Dead Cells (588650) and Ravenswatch (2071280). All four public metadata and review-summary
  responses were available. Observed screenshot counts were 11, 8, 13 and 10 respectively;
  these are dated observations, not fixed expected values.
- Live Streamlit AppTest form also passed against Steam: target plus three comparisons,\n  four table rows, JSON download offered and AI skipped without a key. This checks widget\n  execution, not human visual rendering or downloading screenshot image bytes.\n- Local Markdown links checked.

## Continuous integration

[Tests workflow](https://github.com/canmils/steamlens/actions/workflows/test.yml)
runs the offline suite on Ubuntu and Windows with Python 3.12. The Docker job validates the
explicit AI overlay with a placeholder key, builds/starts the free container, checks HTTP
health and initializes the app with Streamlit AppTest inside the container. Inspect the run
for your commit before claiming it passed. Docker is not installed in the local editing environment.

The base Compose config deliberately does not forward a key. The AI overlay requires one
at runtime. The Docker checks do not make paid model requests or validate model quality.

## Limits

No paid OpenAI call, human visual browser review or native macOS run was performed.
A public Steam response is a snapshot, not a guarantee that future requests work or that metadata
matches every local storefront. Tests do not establish conversion uplift, player comprehension,
market similarity, hosting security or commercial demand. Dependencies use version ranges,
not a fully pinned Python lock. The worked example is fictional; no real-game assets are bundled.

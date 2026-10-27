# SteamLens

Free, open-source Steam store page checklist and side-by-side comparison, with an
optional AI positioning review that uses the user's own OpenAI key. Python and
Streamlit. Local research prototype: it reads public metadata and never forecasts
sales.

## Commands

- Install: `python -m venv .venv && .venv/bin/python -m pip install -r requirements.txt`
- Run: `.venv/bin/python -m streamlit run app/main.py --server.address 127.0.0.1`
- Tests: `.venv/bin/python -m pytest -q`
- Live check: `python scripts/check_live.py`

## Layout

- `app/`: `core.py` (Steam data), `checklist.py`, `positioning.py`, `ai_audit.py`, `main.py` (UI).
- `tests/`: one test file per module.
- `examples/`: fictional worked example. Keep it fictional.

## Rules

- Free features must work without any API key.
- Never present a check as proof of commercial success.
- Never commit keys or `.env` files.

## Coding discipline (Karpathy guidelines)

Before writing, reviewing or refactoring code, load the `karpathy-guidelines` skill
(source: github.com/multica-ai/andrej-karpathy-skills, MIT). The short version:

1. **Read first.** Read the code, docs and tests you will touch before you change anything. Investigate; do not guess.
2. **Think before coding.** State your assumptions. If there is more than one reading of the task, name them. If something is unclear, stop and ask.
3. **Simplicity first.** Write the minimum code for the request. No speculative features, no early abstractions, no new dependency without a stated reason.
4. **Surgical changes.** Touch only what the task needs and match the existing style. Mention unrelated problems; do not fix them silently.
5. **Define success before building.** Turn the task into a check, for example a test that fails first and then passes.
6. **Test the behaviour and fix the root cause.** A green build is not enough. Do not patch symptoms.
7. **Explain what changed and why.** Files touched, the reason, and the checks you actually ran.

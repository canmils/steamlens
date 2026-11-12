# Bounded comparison fetching

Assessed 2026-11-12 against main `09560e30f00c16c461659d64252732ed9118eda3`.

## Problem and decision

`app/main.py` fetched each comparison only after the preceding one finished. One malformed comparison also raised into the outer error handler, hiding the valid target report. Adopt bounded fan-out/fan-in for independent public reads, plus per-comparison validation. Keep the target fetch first, stable input ordering, existing cache, per-request timeouts and a three-entry limit. No automatic Steam retries or new dependencies.

This is an ordinary concurrent data-fetching workflow, not a multi-agent system. LangGraph, CrewAI and a new agent SDK would add orchestration without solving a further demonstrated need. No upstream source code was copied.

## Sources

- Supplied link https://lnkd.in/emRzawkq resolves to [An LLM Compiler for Parallel Function Calling](https://arxiv.org/abs/2312.04511); abstract reviewed. Its results do not establish SteamLens performance.
- [LangGraph workflow guidance](https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/workflows-agents.mdx), reviewed file blob `4b9fceb641a50dd2eb5354be65819d4a8af427bb`: patterns are reference material; no LangGraph dependency or code adopted.
- [Python ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor) is the existing standard-library mechanism.

## Validation

- Baseline: 35 tests passed.
- Regression cases: independent starts with a barrier, at most three reads, stable ordering, duplicate/target skipping, malformed input, timeout partial failure, and Streamlit export with concurrent cached fetches.
- Controlled local benchmark: three independent 80 ms fixture reads, five repetitions. Serial median 240.4 ms; concurrent median 81.7 ms. This measures fixture scheduling only, not live speed or marketing value.
- Live public Steam smoke: Hades plus Hades II, Dead Cells and Ravenswatch returned successfully, no comparison errors, 21.74 seconds for this one run. No live before/after speed comparison; no AI calls or browser image-rendering verification.

Risk: at most three simultaneous comparison lookups creates a small burst rather than serial traffic. The request count is unchanged; do not generalize this approach to rate-limited providers such as MusicBrainz without their own limits. API availability and cache behavior still determine latency. Revert the PR to restore serial fetching.

Existing draft PR #4 is release hardening from an older base. This branch neither edits nor merges it; the maintainer should reconcile its existing conflicts separately.

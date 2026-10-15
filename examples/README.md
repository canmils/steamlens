# Worked example

The two games in [fictional-games.json](fictional-games.json) are invented fixtures,
not real Steam App IDs to enter into the live UI. [fictional-audit.json](fictional-audit.json)
is the deterministic output from the actual audit/checklist/positioning functions.
It contains no AI response and no copied real-game assets.

## What to inspect

- The target's short description is short enough to trigger a review prompt.
- Zero returned screenshots/trailers trigger missing-media checks. In a live API response,
  independently verify the actual listing before declaring that media is absent.
- The comparison lists more languages; this is a descriptive difference, not a localization business case.
- Cooperative-play keywords appear in the comparison description. That does not prove either game
  should change its mechanics or marketing.
- Reviews and price remain unknown, not fabricated numbers.
- The export includes `game`, `competitors`, `findings`, `checklist`, `positioning` and `disclaimer`.
  A successful optional AI request also adds `ai_review`; without it that field is absent.

The regression test recomputes this JSON and checks equality, so the example cannot silently
fall behind the current deterministic implementation. Live data counts will differ.

## Try the real UI

Follow the main README with target `1145360` and comparisons `1145350, 588650, 2071280`.
Expect up to four table rows, a no-key AI skip message and a JSON download. Missing source responses
may produce fewer rows or an error. Inspect source links; do not require fixed review counts or prices.

## Before charging for a review

Have a developer compare the findings against their own listing. Record incorrect observations,
recommendations they would act on, and whether the result improves on their existing checklist.
No measured sales/conversion effect is established by this example or the automated tests.

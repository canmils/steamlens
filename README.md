# SteamLens 🎮

**Free, open-source Steam store page checklist and side-by-side comparison. Optional paid AI review with your own OpenAI key.**

For indie developers and marketers reviewing how their game is presented. Enter a Steam App ID or store URL and up to three comparison games you select. SteamLens reads public metadata; it does not rank likely commercial success.

| Feature | Output | Key needed? |
| --- | --- | --- |
| Store checklist | Description, media, languages, controller and review checks | No |
| Comparison table | Counts, platforms, US price, reviews and release information | No |
| Positioning signals | Configured words/phrases in short descriptions | No |
| AI positioning review | Hypotheses and copy experiments supported by matched store text | Yes, paid OpenAI API |
| JSON export | Target metadata, comparisons, findings/checklist, positioning and successful AI review when present | No for free results |

**Status: local research prototype.** An `ok` check means the element was returned, not that it is effective. No sales, wishlists, conversion forecasts or player research are produced.

## Install on Windows (PowerShell)

Requires Git, Python **3.11 or 3.12** and internet access. Run from the repository root. Activation is unnecessary:

```powershell
git clone https://github.com/canmils/steamlens.git
cd steamlens
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app/main.py --server.address 127.0.0.1
```

## Install on macOS/Linux

```sh
git clone https://github.com/canmils/steamlens.git
cd steamlens
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app/main.py --server.address 127.0.0.1
```

Open http://localhost:8501. Keep the terminal open; Ctrl+C stops the app. Other Python versions may work but are not the supported baseline documented here.

## First use: free comparison

1. Enter `1145360` (Hades) as the target.
2. Enter `1145350, 588650, 2071280` as comparison IDs. These are user-selected examples, not established market peers.
3. Click **Analyze game**. Expect the target name/description, returned screenshots, checklist, four-row comparison table and keyword signals if all requests succeed.
4. Read the source listing links. Compare counts with the returned data; do not interpret more screenshots, reviews or languages as proof of better marketing.
5. Without `OPENAI_API_KEY`, the AI section explicitly says it is skipped.
6. Click **Download JSON audit** and save it outside the checkout. Results are not saved automatically. A refresh or rerun can clear the displayed report; re-analyze if necessary.

Steam data changes. Prices are requested for the US in English and may differ from your local store. Review summaries can be unavailable without preventing the other checks. A failed competitor request shows a warning and leaves available target results usable; a failed target request prevents an audit.

See the [worked example](examples/README.md) and [fictional JSON output](examples/fictional-audit.json). They are deterministic fixtures, not a captured live Steam response or an AI evaluation.

## Optional paid AI review

A ChatGPT subscription does not include API credits. Create your own key at https://platform.openai.com/api-keys. Set it in the **same terminal that starts the app**, then restart. Python launch does not load `.env` automatically.

PowerShell 5.1/7:

```powershell
$secret = Read-Host "OpenAI API key" -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new("", $secret).Password
Remove-Variable secret
.\.venv\Scripts\python.exe -m streamlit run app/main.py --server.address 127.0.0.1
```

Bash:

```bash
read -s -p "OpenAI API key: " OPENAI_API_KEY; echo
export OPENAI_API_KEY
.venv/bin/python -m streamlit run app/main.py --server.address 127.0.0.1
```

With a key and at least one successful comparison, **Analyze game automatically requests the AI review**. There is no separate paid confirmation button or application budget cap. Repeated analyses can incur charges; the SDK can retry once. To return to free-only mode, remove the variable and restart (`Remove-Item Env:OPENAI_API_KEY` in PowerShell; `unset OPENAI_API_KEY` in Bash).

The model is currently `gpt-4.1-mini`, defined in `app/ai_audit.py`; `OPENAI_MODEL` is not a supported override. Verify model access/billing on your account. No key means the free checklist and comparison still work.

AI receives names, App IDs, public short descriptions, excerpts of About text and genres. It does not receive screenshot image bytes. Quote checking tolerates case, spacing and typography differences, but rejects fabricated or stitched quotations. Matching text supports provenance, **not the correctness of the interpretation**. Some or all insights may be rejected. AI failure leaves free results available.

## Free public demo: Streamlit Community Cloud

You can host the free checklist and comparison so people try it without installing anything.

1. Sign in at https://share.streamlit.io with the GitHub account that owns this repository.
2. Click **Create app**, choose this repository, branch `main`, main file `app/main.py`.
3. Under **Advanced settings**, choose Python 3.12. **Leave Secrets empty.**
4. Click **Deploy**. The first start takes a few minutes.

**Do not add `OPENAI_API_KEY` to a public app.** With a key set, every visitor's analysis calls OpenAI automatically on your account, with no budget cap.
Without it, the public demo is free and the AI section says it is skipped.

Steam lookups are cached for one hour. A shared demo can still hit Steam rate limits on busy days; the app then shows an error for that game and nothing else breaks.
A free Streamlit app sleeps after a period without visitors and wakes on the next visit.

## Docker: free by default, AI by explicit opt-in

Requires Docker Engine/Desktop with the Compose plugin. From the repository root:

```sh
docker compose up --build -d
```

Open http://localhost:8501. The base configuration does not pass an OpenAI key to the container, even if one exists in your shell. It binds the published port to localhost.

For AI, set `OPENAI_API_KEY` using the secure terminal instructions above, then use the explicit overlay:

```sh
docker compose -f docker-compose.yml -f docker-compose.ai.yml up --build -d
```

The overlay refuses startup if the key is unset or empty. It passes the key at runtime, not during the image build. Do not paste rendered Compose configuration or environment inspection output into issues; they can reveal secrets. The key is available to people who control the Docker host.

To switch the container back to free-only mode:

```sh
docker compose up --build -d --force-recreate
```

To stop/remove the container: `docker compose down`. No server-side reports volume is needed: keep JSON files downloaded through your browser. See [verification](ONBOARDING_CHECKS.md) for actual Docker test coverage.

## Limits and data handling

- Public metadata can be incomplete or unavailable. Absence from an API response is not definitive proof of absence on the actual page.
- Checklist thresholds are review prompts, not conversion benchmarks or an exhaustive Steam approval checklist. Consult current [Steamworks documentation](https://partner.steamgames.com/doc/store) for publishing requirements.
- Competitor similarity, screenshot quality, trailer content and target-player comprehension require human review. Images are displayed, not understood by the model.
- No Steamworks credentials, SteamDB scraping, user-tag analysis or private performance data are used.
- There is no account system, shared history or permanent report library. JSON export contains public source text/URLs, not screenshot image files. Save observations separately if you need a dated comparison.
- The server does not intentionally persist your key, reports or provider output. Keys stay in the running process environment. Use a trusted local machine; do not expose the development server publicly.
- API/hosting costs, third-party data rights and provider policies still apply. This tool does not establish commercial value or guarantee better results than a chatbot.

## Verify

Use the virtual-environment interpreter above in place of `python`:

```sh
python -m pytest -q
```

The offline suite uses fictional data/mocked providers and includes the actual Streamlit form, errors and export wiring. No Steam or OpenAI requests are needed. CI runs on Ubuntu and Windows.

An explicit live, no-key metadata check is available:

```sh
python scripts/check_live.py --live
```

Optional `--output audit.json` saves a JSON result and refuses to overwrite an existing file. This requests public metadata for the four first-use IDs, not AI or screenshot image bytes. It is separate from CI because source availability changes. It does not test visual browser rendering. See [ONBOARDING_CHECKS.md](ONBOARDING_CHECKS.md) for measured results and limits.

## Update and troubleshoot

Stop the app, preserve downloaded reports and inspect `git status`. Keep code edits on your branch. Run `git pull --ff-only`, then repeat your original pip install command and restart. Docker users rebuild with their chosen Compose command. Resolve divergent history rather than discarding local changes.

| Problem | Action |
| --- | --- |
| Python/Git not found | Install prerequisite, reopen terminal and check version |
| Missing module | Install and launch with the same `.venv` interpreter |
| Steam failure/empty data | Check App ID, connectivity and the public listing; retry later, avoid rapid repeated calls |
| Comparison warning | Inspect which game failed; available results are partial |
| AI skipped | Check launch environment and that at least one comparison succeeded |
| AI error | Check billing/model access/network; inspect free results separately |
| Port 8501 in use | Stop the earlier app or use `--server.port 8502` for Python launch |
| Docker AI key missing | Set it in the launch terminal before using the AI overlay |
| Report disappeared | Refresh/rerun is not durable storage; download JSON after analysis |

## Feedback and contribution

Open an [issue](https://github.com/canmils/steamlens/issues) with OS/Python version, commit (`git rev-parse HEAD`), App IDs, exact steps, sanitized error and expected/actual result. Useful suggestions identify a user problem and a small example. Never attach API keys or private company data.

See [CONTRIBUTING.md](CONTRIBUTING.md) for fork → branch → checks → pull request. Evidence of incorrect data or an unhelpful recommendation is more valuable than unsupported claims about improved sales.

## License

[MIT](LICENSE) for code/authored documentation. Third-party Steam text, images and trademarks retain their respective rights.

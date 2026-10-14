# SteamLens 🎮

**Experimental, free, open-source Steam store-page checklist and competitor comparison.** Optional AI positioning review using **your own paid OpenAI API key**.

SteamLens runs **locally on your computer**. There is **no hosted website or account**. It does not edit your Steam page, estimate wishlists/sales, or prove conversion improvements.

## What you can do

- **Free checklist:** inspect descriptions, screenshots, trailers, languages, controller support and public review counts.
- **Free comparison:** compare public listing details with up to three Steam games **you choose**.
- **Free keyword signals:** see literal terms detected in short descriptions; missing terms do not imply missing gameplay.
- **Optional AI review:** generate 2–3 *hypotheses* about differences in public store copy. Matched evidence quotes do not prove the interpretation.
- **Export:** download the audit as JSON, including the AI review if one was generated.

## Quick start — Windows PowerShell

Install [Python 3.10+](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads), then open PowerShell:

```powershell
git clone https://github.com/canmils/steamlens.git
cd steamlens
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app/main.py
```

Open **http://localhost:8501** if your browser does not open automatically. Enter `1145360` (Hades); optional competitors: `1145350, 588650, 2071280`. Click **Analyze game**. You do **not** need an OpenAI key for the free features. Stop the app with **Ctrl+C**.

If PowerShell blocks activation, you can run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.\.venv\Scripts\python.exe -m streamlit run app/main.py` without activating the environment.

## macOS / Linux

Requires Python 3.10+ and Git:

```bash
git clone https://github.com/canmils/steamlens.git
cd steamlens
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app/main.py
```

Open **http://localhost:8501**. On some Linux distributions you may need to install the Python venv package first.

## Optional AI review (paid API)

A ChatGPT subscription **does not** include OpenAI API credits. Get an API key from https://platform.openai.com/api-keys and check API billing. The AI review requires at least one competitor and sends public game names, App IDs, genres, short descriptions and excerpts of About text to OpenAI; **no screenshots** are sent.

**Windows PowerShell:** stop the app, then in the same terminal:

```powershell
$env:OPENAI_API_KEY = Read-Host -Prompt "Enter OpenAI API key" -MaskInput
python -m streamlit run app/main.py
```

**macOS / Linux:** set `OPENAI_API_KEY` in the terminal environment before starting Streamlit. Avoid saving the key in shell history, committed files or screenshots. Use a private terminal input method.

API requests may incur charges. **Never post API keys in GitHub Issues, pull requests, screenshots or exported logs.** Revoke any accidentally disclosed key.

## Docker alternative

If Docker Compose is installed:

```bash
docker compose up --build
```

Open **http://localhost:8501**. Docker Compose binds to localhost only. The provided Compose configuration does **not** forward `OPENAI_API_KEY` by default, so this starts the **free** workflow. For AI, use the Python instructions above or configure a private, untracked container environment securely.

## Share feedback or ask for help

We want feedback from indie developers, publishers and Steam marketers. **You do not need programming skills to help.**

| What you want to do | Where to go |
| --- | --- |
| Report a bug or incorrect Steam data | [Report a bug](https://github.com/canmils/steamlens/issues/new?template=bug_report.yml) |
| Suggest an improvement | [Suggest an idea](https://github.com/canmils/steamlens/issues/new?template=feature_request.yml) |
| Tell us whether an audit was useful | [Share beta feedback](https://github.com/canmils/steamlens/issues/new?template=beta_feedback.yml) |
| Ask a question | [Open an issue](https://github.com/canmils/steamlens/issues/new/choose) |
| Fix code or documentation | Read [CONTRIBUTING.md](CONTRIBUTING.md), then open a [pull request](https://github.com/canmils/steamlens/pulls) |

A free GitHub account is required to post Issues or PRs. For useful feedback, tell us your **Steam App ID**, what you expected, what happened, and whether you would take action based on the result. **Please do not include private Steamworks metrics, credentials or personal data.**

This beta is deliberately **feature-frozen** until we review feedback from 5–10 real users. Bugs, documentation corrections and security fixes are welcome; larger features should be discussed in an Issue first. Maintainers review contributions; submitting a PR does not guarantee merge.

## Development and testing

```bash
python -m pytest -q
python -m compileall -q app
```

GitHub Actions runs automated tests on pull requests and pushes to `main`. See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow and [beta release gate](docs/BETA_RELEASE.md) for outstanding verification before the v0.5.1 pre-release.

## Data, privacy and limitations

- Public data comes from Steam's store endpoints. Availability, accuracy and usage terms can change. The default request locale is **English / US**; prices may differ in your region.
- The free checklist and comparison **do not call OpenAI**. SteamLens fetches game information from Steam.
- If AI is enabled, SteamLens sends the public text described above to OpenAI. It does not intentionally save API keys in files or exported JSON; the key stays in the process environment. Use on a trusted local computer and **do not expose the development server publicly**.
- AI output is fallible. Quotes are matched after limited normalization; conclusions are **not fact-checked**.
- Checklist thresholds are review prompts, not scientifically validated optimization targets. **“OK” means the element is present, not effective.**
- Competitors are chosen by the user; SteamLens does not determine competitive similarity.
- No access to private Steamworks analytics, wishlists, sales, conversion rates or player behavior. No image understanding, SteamDB scraping, or automatic Steam listing updates.
- SteamLens is an **experimental local research tool**, not a hosted production service. Please respect Steam and OpenAI terms and rate limits.

## License

[MIT](LICENSE). Third-party game assets, data, names and trademarks remain the property of their respective owners.

# SteamLens 🎮

**Open-source Steam store positioning audit powered by a user-supplied OpenAI API key.**

> **Required: OpenAI API key.** SteamLens v0.4 cannot generate an AI audit without one. The OpenAI API is a paid service and usage may incur charges. A ChatGPT subscription does not automatically include API credits.

SteamLens fetches public Steam store metadata, compares a target game with up to three user-selected games, and requests 2–3 AI-generated positioning hypotheses backed by exact quotations from public descriptions. It also displays descriptive metadata checks and experimental keyword signals.

## Requirements

- Python 3.10+ (or Docker)
- Internet connection to Steam and OpenAI
- **Your own OpenAI API key with API access and billing configured.** Create one at https://platform.openai.com/api-keys . Keep it private; **never put your key in GitHub, screenshots, issues, or configuration files committed to Git.**
- AI model: `gpt-4.1-mini`. Availability and pricing may change; consult OpenAI's pricing page before use.

## Run on Windows (PowerShell)

```powershell
git clone https://github.com/canmils/steamlens.git
cd steamlens
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:OPENAI_API_KEY = Read-Host -Prompt "Enter API key" -MaskInput
python -m streamlit run app/main.py
```

Open http://localhost:8501 . Set the API key in the PowerShell session **before starting Streamlit**:\n\n```powershell\n$env:OPENAI_API_KEY = Read-Host -Prompt "Enter API key" -MaskInput\npython -m streamlit run app/main.py\n```\n\nEnter a Steam URL or App ID (example: `1145360`), optionally enter up to three competitor App IDs (example: `1145350, 588650, 2071280`), then select **Analyze game**.

To run tests: `python -m pytest -q`.

## Docker

```bash
docker compose up --build
```

Set `OPENAI_API_KEY` in the container runtime environment before launching (for example, via an untracked local environment configuration). Never embed it in the image or commit it to the repository.

## Privacy, cost, and limitations

- SteamLens uses the key only to call OpenAI for the submitted audit. It does **not intentionally persist the key** in files, exported JSON, or logs. The key remains in the server process environment while SteamLens is running. Use this local app only on a machine/network you trust; do not expose the development server publicly.
- SteamLens sends the target and competitor **game names, App IDs, public short descriptions, excerpts of the About text, and genres** to OpenAI. It does not send screenshot image bytes in v0.4.
- API usage may incur charges on each analysis. Check provider billing and data handling policies before use.
- AI output is fallible. Each displayed AI finding must contain a verbatim quote from the supplied public text, but **a correct quote does not prove the interpretation**.
- No sales, wishlists, conversion predictions, player reaction measurements, Steamworks access, or image understanding.
- Competitors are selected by the user; the app does not establish market similarity.
- No SteamDB scraping. The public Steam `appdetails` endpoint may change or become unavailable; respect rate limits and usage terms.
- This is a local research prototype, **not** a production-ready hosted service.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bugs and PRs welcome. Do not share API keys in bug reports.

## License

MIT. Third-party data, images, and trademarks remain owned by their respective owners.

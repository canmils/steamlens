# SteamLens 🎮

**Free, open-source Steam store page checklist and side-by-side comparison. Optional AI review with your own OpenAI API key.**

Enter your game's Steam App ID and up to three games you compete with. SteamLens reads public Steam data and shows:

- **Store page checklist (free, no key):** short description length, screenshots, trailer, languages, controller support and user reviews, with a suggested action for each item that needs attention.
- **Side-by-side numbers (free, no key):** description length, screenshots, trailers, languages, platforms, price, reviews and release date for your game and the games you picked.
- **Keyword signals (free, no key):** which positioning words (combat, co-op, roguelike, myth...) appear in each short description.
- **AI positioning review (optional, paid):** 2-3 hypotheses comparing your store text with a competitor's. Each one must quote the public text word for word or it is hidden.


## Quick start on Windows (PowerShell)

```powershell
git clone https://github.com/canmils/steamlens.git
cd steamlens
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app/main.py
```

Open http://localhost:8501 . Try App ID `1145360` (Hades) with comparison games `1145350, 588650, 2071280`.

### Optional: enable the AI review

The AI review uses the OpenAI API, which is a paid service (a ChatGPT subscription does not include API credits). Create a key at https://platform.openai.com/api-keys and set it in the same PowerShell window **before** starting the app:

```powershell
$env:OPENAI_API_KEY = Read-Host -Prompt "Enter API key" -MaskInput
python -m streamlit run app/main.py
```

Never put your key in GitHub, screenshots, issues or committed files.

To run tests: `python -m pytest -q`.

## Feedback wanted

This is an early prototype. The most useful feedback right now:

1. **Indie developers and marketers:** which store page checks would you actually use? What is missing or wrong?
2. Games where the data looks wrong (please include the App ID).
3. Whether the AI review says anything you could not get by pasting your store text into a chatbot.

Open an [issue](https://github.com/canmils/steamlens/issues) or a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Requirements

- Python 3.10+ (or Docker)
- Internet connection to Steam (and to OpenAI only if you use the AI review)

## Docker

```bash
docker compose up --build
```

To use the AI review, set `OPENAI_API_KEY` in the container runtime environment before launching (for example, via an untracked local environment configuration). Never embed it in the image or commit it to the repository.

## Privacy, cost, and limitations

- The checklist and comparison need no key and send nothing to OpenAI.
- SteamLens uses the key only to call OpenAI for the submitted audit. It does **not intentionally persist the key** in files, exported JSON, or logs. The key remains in the server process environment while SteamLens is running. Use this local app only on a machine/network you trust; do not expose the development server publicly.
- SteamLens sends the target and competitor **game names, App IDs, public short descriptions, excerpts of the About text, and genres** to OpenAI. It does not send screenshot image bytes.
- API usage may incur charges on each analysis. Check provider billing and data handling policies before use.
- AI output is fallible. Each displayed AI finding must contain a verbatim quote from the supplied public text, but **a correct quote does not prove the interpretation**.
- No sales, wishlists, conversion predictions, player reaction measurements, Steamworks access, user tags or image understanding.
- A checklist item marked as present means the element exists, not that it works well.
- Competitors are selected by the user; the app does not establish market similarity.
- No SteamDB scraping. The public Steam `appdetails` endpoint may change or become unavailable; respect rate limits and usage terms.
- This is a local research prototype, **not** a production-ready hosted service.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bugs and PRs welcome. Do not share API keys in bug reports.

## License

MIT. Third-party data, images, and trademarks remain owned by their respective owners.

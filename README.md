# SteamLens 🎮

**Experimental, open-source, local-first Steam marketing audit.**

Enter a public Steam store URL or App ID. SteamLens retrieves public store metadata, runs explainable heuristic checks, optionally compares up to three manually chosen games, and exports findings to JSON.

## Quick start (Docker)

```bash
docker compose up --build
```

Open **http://localhost:8501**.

## Quick start (Python)

```bash
python -m venv .venv
# Activate the environment using your operating system's normal command
pip install -r requirements.txt
streamlit run app/main.py
```

## What v0.1 does not do

- No AI agents or model integrations yet.
- No authenticated Steamworks data, wishlist counts, sales estimates or conversion predictions.
- No scraping of SteamDB.
- No automatic image quality evaluation.
- No persistent projects or campaign tracking yet.
- Does not modify Steam listings or send messages to creators.

## Data-source caveat

The prototype uses the public Steam store `appdetails` endpoint. Availability, terms, fields and rate limits may change. Confirm permitted use and caching before distributing a hosted production service. Respect rate limits. Do not use this project to bypass access controls.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bugs and feature requests are welcome. All pull requests require tests and maintainer review.

## License

MIT. Third-party data, images and trademarks remain owned by their respective owners.

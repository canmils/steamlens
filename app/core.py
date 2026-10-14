import re
from urllib.parse import urlparse
from html import unescape
import requests

STORE_API = "https://store.steampowered.com/api/appdetails"

def app_id(value: str) -> int:
    value = value.strip()
    if re.fullmatch(r"\d{1,12}", value):
        return int(value)
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or parsed.hostname != "store.steampowered.com":
        raise ValueError("Enter a Steam store URL or numeric App ID.")
    match = re.match(r"^/app/(\d+)(?:/|$)", parsed.path)
    if not match:
        raise ValueError("Expected a URL like https://store.steampowered.com/app/1145360/")
    return int(match.group(1))

def clean(value):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()

def fetch_game(identifier: int) -> dict:
    response = requests.get(STORE_API, params={"appids": identifier, "cc": "us", "l": "english"},
                            timeout=12, headers={"User-Agent": "SteamLens/0.2 (open-source research tool)"})
    response.raise_for_status()
    result = response.json().get(str(identifier), {})
    if not result.get("success") or not isinstance(result.get("data"), dict):
        raise ValueError(f"Steam did not return public store data for app {identifier}.")
    data = result["data"]
    return {
        "app_id": identifier, "name": data.get("name", "Unknown"), "type": data.get("type"),
        "short_description": clean(data.get("short_description")),
        "about_the_game": clean(data.get("about_the_game")),
        "header_image": data.get("header_image"),
        "screenshots": [s["path_thumbnail"] for s in data.get("screenshots", []) if s.get("path_thumbnail")],
        "genres": [g["description"] for g in data.get("genres", []) if g.get("description")],
        "categories": [c["description"] for c in data.get("categories", []) if c.get("description")],
        "developers": data.get("developers", []),
        "release_date": (data.get("release_date") or {}).get("date"),
        "coming_soon": (data.get("release_date") or {}).get("coming_soon"),
        "price_overview": data.get("price_overview"),
        "source_url": f"https://store.steampowered.com/app/{identifier}/",
    }

def finding(code, title, severity, observation, recommendation, evidence):
    return {"id": code, "title": title, "severity": severity, "observation": observation,
            "recommendation": recommendation, "evidence": evidence, "type": "heuristic",
            "confidence": "Descriptive check only; marketing impact not established"}

def audit(game: dict, competitors: list[dict] | None = None) -> dict:
    findings = []
    description = clean(game.get("short_description"))
    screenshots = game.get("screenshots") or []
    genres = game.get("genres") or []
    categories = game.get("categories") or []
    if not description:
        findings.append(finding("missing-description", "Short description missing", "high",
            "The public store response contains no short description.",
            "Verify the listing and add a concise description of the player's main activity and distinctive hook.",
            {"field": "short_description", "value": ""}))
    elif len(description) < 80:
        findings.append(finding("short-description", "Short description needs review", "medium",
            f"The short description contains {len(description)} characters; this is a review trigger, not a proven optimal length.",
            "Check whether the text explains what players do and what makes the game different.",
            {"field": "short_description", "length": len(description), "text": description}))
    else:
        findings.append(finding("description-present", "Short description available", "info",
            f"The public store response contains a {len(description)}-character short description.",
            "Ask target players to describe the game after reading only this text; check for mismatches.",
            {"field": "short_description", "text": description}))
    if len(screenshots) < 5:
        findings.append(finding("screenshots", "Few screenshots returned", "medium",
            f"The public endpoint returned {len(screenshots)} screenshots.",
            "Verify the listing and consider showing more representative gameplay moments.",
            {"field": "screenshots", "count": len(screenshots)}))
    else:
        findings.append(finding("screenshots-present", "Screenshot review", "info",
            f"The public endpoint returned {len(screenshots)} screenshots.",
            "Review the first five in order: can a new player identify the core gameplay and visual identity?",
            {"field": "screenshots", "count": len(screenshots), "first_five": screenshots[:5]}))
    if not genres:
        findings.append(finding("genres", "Genre data missing", "low",
            "No genre metadata was returned.", "Check the game's categorization in Steamworks.",
            {"field": "genres", "value": []}))
    if not categories:
        findings.append(finding("categories", "Categories not returned", "low",
            "No category metadata was returned.", "Verify the public listing and supported features.",
            {"field": "categories", "value": []}))
    comparisons = []
    for other in competitors or []:
        shared = sorted(set(genres) & set(other.get("genres") or []))
        comparisons.append({
            "app_id": other["app_id"], "name": other["name"], "shared_genres": shared,
            "screenshot_count": len(other.get("screenshots") or []),
            "description_length": len(clean(other.get("short_description"))),
            "genres": other.get("genres") or [],
            "short_description": clean(other.get("short_description")),
            "source_url": other.get("source_url", ""),
            "note": "Descriptive comparison; not a conversion or quality ranking."
        })
    if comparisons:
        findings.append(finding("comparison-review", "Review competitor positioning", "info",
            f"Compared against {len(comparisons)} user-selected game(s); genre overlap alone does not establish market similarity.",
            "Compare the opening descriptions and first screenshots side by side; document differences in audience promise.",
            {"field": "competitors", "names": [c["name"] for c in comparisons]}))
    return {"game": game, "competitors": comparisons, "findings": findings,
            "disclaimer": "Public store metadata and descriptive heuristics only. No sales, wishlist, conversion or player estimates. Data may be incomplete."}

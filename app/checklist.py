"""Store page checklist: deterministic checks from public Steam data. Works without an API key."""
import re

SHORT_DESCRIPTION_MAX = 300   # Steam store editor limit
MIN_SCREENSHOTS = 5           # Steam minimum for a store page
TARGET_SCREENSHOTS = 8        # common checklist recommendation


def parse_languages(raw):
    """Return (all languages, languages with full audio) from Steam's supported_languages HTML."""
    if not raw:
        return [], []
    head = re.split(r"<br\s*/?>", raw, maxsplit=1)[0]
    langs, audio = [], []
    for part in head.split(","):
        has_audio = "*" in part
        name = re.sub(r"<[^>]+>|\*", "", part).strip()
        if name:
            langs.append(name)
            if has_audio:
                audio.append(name)
    return langs, audio


def metrics(game):
    """Comparable numbers for one game. Missing data stays None, never guessed."""
    reviews = game.get("reviews") or {}
    total = reviews.get("total_reviews")
    positive = reviews.get("total_positive")
    platforms = game.get("platforms") or {}
    price = game.get("price_overview") or {}
    return {
        "name": game.get("name", "Unknown"),
        "short_description_chars": len(game.get("short_description") or ""),
        "about_words": len((game.get("about_the_game") or "").split()),
        "screenshots": len(game.get("screenshots") or []),
        "trailers": game.get("trailer_count"),
        "languages": len(game.get("languages") or []),
        "full_audio_languages": len(game.get("audio_languages") or []),
        "platforms": ", ".join(p.capitalize() for p in ("windows", "mac", "linux") if platforms.get(p)) or None,
        "controller_support": game.get("controller_support") or "none listed",
        "achievements": game.get("achievements"),
        "price": "Free" if game.get("is_free") else price.get("final_formatted") or None,
        "reviews_total": total,
        "reviews_positive_pct": round(100 * positive / total) if total and positive is not None else None,
        "review_summary": reviews.get("review_score_desc"),
        "release": "Coming soon" if game.get("coming_soon") else game.get("release_date"),
    }


def check(code, label, status, detail, action=""):
    return {"id": code, "check": label, "status": status, "detail": detail, "action": action}


def store_checklist(game, competitors=None):
    """Checks for the target game. status: ok, review, missing."""
    m = metrics(game)
    peers = [metrics(c) for c in competitors or []]
    out = []

    n = m["short_description_chars"]
    if n == 0:
        out.append(check("short-description", "Short description", "missing", "No short description returned.",
                         "Write one or two sentences: what the player does and what makes the game different."))
    elif n < 120:
        out.append(check("short-description", "Short description", "review",
                         f"{n} of {SHORT_DESCRIPTION_MAX} characters used.",
                         "There is room to name the core activity, the hook and the genre."))
    else:
        out.append(check("short-description", "Short description", "ok",
                         f"{n} of {SHORT_DESCRIPTION_MAX} characters used."))

    s = m["screenshots"]
    if s < MIN_SCREENSHOTS:
        out.append(check("screenshots", "Screenshots", "missing", f"{s} screenshots; Steam requires at least {MIN_SCREENSHOTS}.",
                         "Add gameplay screenshots until there are at least 5."))
    elif s < TARGET_SCREENSHOTS:
        out.append(check("screenshots", "Screenshots", "review", f"{s} screenshots.",
                         f"Many store page guides suggest {TARGET_SCREENSHOTS}-10. Check that the first 4 show real gameplay."))
    else:
        out.append(check("screenshots", "Screenshots", "ok", f"{s} screenshots.",
                         "Check that the first 4 show real gameplay, not menus or logos."))

    t = m["trailers"]
    if t is not None:
        if t == 0:
            out.append(check("trailer", "Trailer", "missing", "No trailer on the store page.",
                             "Add a gameplay trailer and place it first in the media."))
        else:
            out.append(check("trailer", "Trailer", "ok", f"{t} video(s).",
                             "Check that real gameplay appears in the first seconds of the first video."))

    langs = m["languages"]
    if langs:
        detail = f"{langs} languages, {m['full_audio_languages']} with full audio."
        peer_langs = [p["languages"] for p in peers if p["languages"]]
        if peer_langs and langs < min(peer_langs):
            out.append(check("languages", "Languages", "review", detail + f" Every compared game lists more (lowest: {min(peer_langs)}).",
                             "Check whether more interface or subtitle translations are realistic for your audience."))
        else:
            out.append(check("languages", "Languages", "ok", detail))

    if m["controller_support"] == "none listed":
        out.append(check("controller", "Controller support", "review", "No controller support listed.",
                         "If the game works with a controller, declare it in Steamworks. It also helps on Steam Deck."))
    else:
        out.append(check("controller", "Controller support", "ok", f"Listed as {m['controller_support']}."))

    if m["reviews_total"] is not None:
        if m["reviews_total"] < 10:
            out.append(check("reviews", "User reviews", "review", f"{m['reviews_total']} reviews.",
                             "Below 10 reviews, Steam shows no review score on the store page."))
        else:
            out.append(check("reviews", "User reviews", "ok",
                             f"{m['review_summary'] or 'Score'}: {m['reviews_positive_pct']}% positive of {m['reviews_total']:,}."))

    return {"checks": out, "table": [m, *peers],
            "note": "Checks use public Steam data only. 'ok' means the item is present, not that it works well."}

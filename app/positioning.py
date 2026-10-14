"""Transparent keyword-based positioning signals. Not semantic understanding."""
import re

SIGNALS = {
    "Combat": ("combat", "fight", "battle", "hack and slash", "souls"),
    "Exploration": ("explore", "exploration", "world", "castle", "discover"),
    "Roguelike progression": ("roguelike", "rogue-like", "roguelite", "rogue-lite", "dungeon crawler", "no checkpoints", "die", "repeat"),
    "Myth and folklore": ("underworld", "god", "gods", "titan", "folk tales", "legends", "myth"),
    "Magic": ("magic", "sorcery", "spell", "witch"),
    "Cooperative play": ("co-op", "cooperative", "multiplayer"),
    "Story": ("story", "narrative", "characters", "tale"),
    "Crafting": ("craft", "build", "survival"),
}

def signals(text: str) -> dict[str, list[str]]:
    """Match whole words/phrases and return literal evidence from description."""
    normalized = re.sub(r"\s+", " ", text or "").lower()
    found = {}
    for label, terms in SIGNALS.items():
        matches = []
        for term in terms:
            pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
            if re.search(pattern, normalized):
                matches.append(term)
        if matches:
            found[label] = matches
    return found

def positioning(game: dict, competitors: list[dict]) -> dict:
    main = signals(game.get("short_description") or "")
    rows = [{"name": game.get("name", "Game"), "app_id": game.get("app_id"),
             "signals": main, "source": "short_description"}]
    for competitor in competitors:
        rows.append({"name": competitor.get("name", "Game"), "app_id": competitor.get("app_id"),
                     "signals": signals(competitor.get("short_description") or ""),
                     "source": "short_description"})
    peer_signals = set().union(*(set(row["signals"]) for row in rows[1:])) if len(rows) > 1 else set()
    return {"games": rows, "shared": sorted(set(main) & peer_signals),
            "main_only": sorted(set(main) - peer_signals),
            "peer_only": sorted(peer_signals - set(main)),
            "method": "Literal keyword matching of public English short descriptions. Missing signal does not mean missing gameplay feature. No performance inference."}

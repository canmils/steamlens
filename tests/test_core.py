import pytest
from app.core import app_id, audit, clean

def test_app_id():
    assert app_id("1145360") == 1145360
    assert app_id("https://store.steampowered.com/app/1145360/Hades/") == 1145360

@pytest.mark.parametrize("bad", ["https://evil.com/app/123", "https://store.steampowered.com.evil.com/app/123", "file:///etc/passwd", "abc"])
def test_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        app_id(bad)

def test_clean():
    assert clean("<b>Play</b> &amp; win") == "Play & win"

def test_audit_missing_fields():
    game = {"app_id": 1, "name": "Example", "short_description": "Short", "screenshots": [], "genres": []}
    result = audit(game)
    assert any(f["id"] == "short-description" for f in result["findings"])
    assert all("evidence" in f for f in result["findings"])

def test_complete_game_has_review_findings():
    game = {"app_id": 1, "name": "Example", "short_description": "A" * 120,
            "screenshots": ["image"] * 6, "genres": ["Action"], "categories": ["Single-player"]}
    result = audit(game)
    assert {f["id"] for f in result["findings"]} >= {"description-present", "screenshots-present"}

def test_competitor_comparison():
    game = {"app_id": 1, "name": "Example", "short_description": "A" * 120,
            "screenshots": ["image"] * 6, "genres": ["Action"], "categories": ["Single-player"]}
    other = {"app_id": 2, "name": "Other", "short_description": "<b>Action</b> game",
             "screenshots": ["image"], "genres": ["Action", "Indie"]}
    result = audit(game, [other])
    assert result["competitors"][0]["shared_genres"] == ["Action"]
    assert result["competitors"][0]["description_length"] == len("Action game")

from app.positioning import signals, positioning

def test_positioning_matches_phrases():
    result = signals("Fight the Titan of Time with dark sorcery in the Underworld.")
    assert result["Combat"] == ["fight"]
    assert "sorcery" in result["Magic"]
    assert "titan" in result["Myth and folklore"]

def test_positioning_word_boundaries():
    assert "Crafting" not in signals("The spacecraft travels quickly.")

def test_positioning_competitor_differences():
    target = {"app_id": 1, "name": "Target", "short_description": "Fight in the underworld."}
    other = {"app_id": 2, "name": "Other", "short_description": "Explore a castle with friends in co-op."}
    result = positioning(target, [other])
    assert "Combat" in result["main_only"]
    assert "Cooperative play" in result["peer_only"]
    assert len(result["games"]) == 2

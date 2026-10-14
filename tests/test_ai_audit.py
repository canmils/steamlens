from types import SimpleNamespace
import pytest
from app.ai_audit import ai_audit, validate_report, evidence_games

def fake_client(report):
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=report, refusal=None), finish_reason="stop")])
    class Completion:
        def create(self, **kwargs):
            assert kwargs["response_format"]["type"] == "json_schema"
            assert kwargs["response_format"]["json_schema"]["strict"] is True
            return response
    return SimpleNamespace(chat=SimpleNamespace(completions=Completion()))

GAME = {"app_id": 1, "name": "Target", "short_description": "Fight through the underworld and escape the gods.", "genres": ["Action"]}
OTHER = {"app_id": 2, "name": "Rival", "short_description": "Explore a haunted castle with friends.", "genres": ["Action"]}

def test_key_required():
    with pytest.raises(ValueError, match="required"):
        ai_audit(GAME, [OTHER], "")

def test_ai_grounded_output():
    import json
    items = [
        {"title": "Combat hook", "interpretation": "The target emphasizes combat.", "action": "Test clearer copy.",
         "evidence_quote": "Fight through the underworld", "evidence_app_id": "1"},
        {"title": "Competitor angle", "interpretation": "A rival emphasizes exploration.", "action": "Compare store copy.",
         "evidence_quote": "Explore a haunted castle", "evidence_app_id": "2"},
    ]
    result = ai_audit(GAME, [OTHER], "test-key", client=fake_client(json.dumps({"insights": items})))
    assert len(result["insights"]) == 2
    assert "test-key" not in str(result)

def test_ai_rejects_fabricated_quote():
    games = evidence_games(GAME, [OTHER])
    items = [{"title": "A", "interpretation": "B", "action": "C",
              "evidence_quote": "No such evidence here", "evidence_app_id": "1"}] * 2
    with pytest.raises(ValueError, match="unsupported evidence"):
        validate_report({"insights": items}, games)

def test_quote_tolerates_typography_case_and_spacing():
    game = {**GAME, "short_description": "Defy the god of the dead — hack and slash out of the Underworld’s depths."}
    items = [
        {"title": "A", "interpretation": "B", "action": "C",
         "evidence_quote": "“defy the god of the dead - hack  and slash”", "evidence_app_id": "1"},
        {"title": "A", "interpretation": "B", "action": "C",
         "evidence_quote": "Underworld's depths", "evidence_app_id": " 1 "},
    ]
    insights, dropped = validate_report({"insights": items}, evidence_games(game, []))
    assert len(insights) == 2 and dropped == 0

def test_one_bad_quote_drops_only_that_insight():
    games = evidence_games(GAME, [OTHER])
    good = {"title": "A", "interpretation": "B", "action": "C",
            "evidence_quote": "Explore a haunted castle", "evidence_app_id": "2"}
    bad = {**good, "evidence_app_id": "1"}
    insights, dropped = validate_report({"insights": [good, bad]}, games)
    assert insights == [good] and dropped == 1

def test_stitched_quotes_are_rejected():
    games = evidence_games(GAME, [OTHER])
    good = {"title": "A", "interpretation": "B", "action": "C",
            "evidence_quote": "Explore a haunted castle", "evidence_app_id": "2"}
    stitched = {**good, "evidence_quote": "Fight through ... underworld and ... escape the gods", "evidence_app_id": "1"}
    insights, dropped = validate_report({"insights": [good, stitched]}, games)
    assert dropped == 1

def test_paraphrase_still_rejected():
    games = evidence_games(GAME, [OTHER])
    item = {"title": "A", "interpretation": "B", "action": "C",
            "evidence_quote": "Battle through the underworld", "evidence_app_id": "1"}
    with pytest.raises(ValueError, match="unsupported evidence"):
        validate_report({"insights": [item, item]}, games)

def test_prompt_names_target_and_avoids_placeholder():
    import json
    seen = {}
    items = [{"title": "A", "interpretation": "B", "action": "C",
              "evidence_quote": "Explore a haunted castle", "evidence_app_id": "2"}] * 2
    client = fake_client(json.dumps({"insights": items}))
    original = client.chat.completions.create
    def spy(**kwargs):
        seen.update(kwargs)
        return original(**kwargs)
    client.chat.completions.create = spy
    ai_audit(GAME, [OTHER], "key", client=client)
    system = seen["messages"][0]["content"]
    assert "Target" in system and "never write the words TARGET" in system

def test_ai_rejects_invalid_shape():
    with pytest.raises(ValueError, match="2–3"):
        validate_report({"insights": []}, evidence_games(GAME, []))

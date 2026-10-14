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

def test_ai_rejects_invalid_shape():
    with pytest.raises(ValueError, match="2–3"):
        validate_report({"insights": []}, evidence_games(GAME, []))

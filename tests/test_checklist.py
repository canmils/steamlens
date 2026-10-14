from app.checklist import parse_languages, metrics, store_checklist

HADES_LANGS = ("English<strong>*</strong>, French, Italian, German, Spanish - Spain<br>"
               "<strong>*</strong>languages with full audio support")

def game(**extra):
    base = {"app_id": 1, "name": "Target", "short_description": "A" * 150, "about_the_game": "one two three",
            "screenshots": ["s"] * 9, "trailer_count": 2, "languages": ["English", "French"],
            "audio_languages": ["English"], "controller_support": "full", "is_free": False,
            "price_overview": {"final_formatted": "$9.99"}, "platforms": {"windows": True, "linux": True},
            "reviews": {"total_reviews": 200, "total_positive": 180, "review_score_desc": "Very Positive"},
            "release_date": "Sep 17, 2020", "coming_soon": False}
    base.update(extra)
    return base

def status(result, code):
    return next(c["status"] for c in result["checks"] if c["id"] == code)

def test_parse_languages():
    langs, audio = parse_languages(HADES_LANGS)
    assert langs == ["English", "French", "Italian", "German", "Spanish - Spain"]
    assert audio == ["English"]
    assert parse_languages(None) == ([], [])

def test_metrics():
    m = metrics(game())
    assert m["reviews_positive_pct"] == 90
    assert m["platforms"] == "Windows, Linux"
    assert m["price"] == "$9.99"
    assert m["about_words"] == 3
    assert metrics(game(is_free=True))["price"] == "Free"
    assert metrics(game(reviews=None))["reviews_positive_pct"] is None

def test_complete_page_is_ok():
    result = store_checklist(game())
    assert all(c["status"] == "ok" for c in result["checks"])

def test_problems_are_flagged():
    result = store_checklist(game(short_description="", screenshots=["s"] * 3, trailer_count=0,
                                  controller_support=None, reviews={"total_reviews": 4, "total_positive": 4}))
    assert status(result, "short-description") == "missing"
    assert status(result, "screenshots") == "missing"
    assert status(result, "trailer") == "missing"
    assert status(result, "controller") == "review"
    assert status(result, "reviews") == "review"

def test_languages_compared_with_competitors():
    rival = game(app_id=2, name="Rival", languages=["a", "b", "c", "d"])
    result = store_checklist(game(), [rival])
    assert status(result, "languages") == "review"
    assert [row["name"] for row in result["table"]] == ["Target", "Rival"]

def test_missing_data_is_not_guessed():
    result = store_checklist(game(trailer_count=None, reviews=None, languages=[]))
    ids = {c["id"] for c in result["checks"]}
    assert not ids & {"trailer", "reviews", "languages"}

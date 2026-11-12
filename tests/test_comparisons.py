from threading import Barrier, Lock

import requests

from app.core import fetch_comparisons


def test_comparisons_overlap_and_keep_input_order():
    # All three must start before any finishes; a serial implementation fails.
    started = Barrier(3, timeout=3)
    lock = Lock()
    calls = []

    def fetch(identifier):
        with lock:
            calls.append(identifier)
        started.wait()
        return {"app_id": identifier}

    games, errors = fetch_comparisons(1, ["2", "3", "4", "5"], fetcher=fetch)
    assert [g["app_id"] for g in games] == [2, 3, 4]
    assert sorted(calls) == [2, 3, 4]
    assert errors == []


def test_duplicate_target_and_invalid_comparison_do_not_break_successes():
    calls = []

    def fetch(identifier):
        calls.append(identifier)
        return {"app_id": identifier}

    games, errors = fetch_comparisons(1, ["bad", "2", "2"], fetcher=fetch)
    assert games == [{"app_id": 2}]
    assert calls == [2]
    assert len(errors) == 1 and "bad" in errors[0]
    assert fetch_comparisons(1, ["1", "1"], fetcher=fetch) == ([], [])
    assert fetch_comparisons(1, [], fetcher=fetch) == ([], [])


def test_failed_source_is_reported_once_and_does_not_drop_other_games():
    calls = []

    def fetch(identifier):
        calls.append(identifier)
        if identifier == 2:
            raise requests.Timeout("Fixture Steam timeout")
        return {"app_id": identifier}

    games, errors = fetch_comparisons(1, ["2", "3"], fetcher=fetch)
    assert games == [{"app_id": 3}]
    assert sorted(calls) == [2, 3]
    assert len(errors) == 1 and "Comparison game 2" in errors[0]

import json
import os
from pathlib import Path
from unittest.mock import patch

import subprocess
import sys

import pytest
import requests
import streamlit as st
from streamlit.testing.v1 import AppTest
from app.core import audit
from app.checklist import store_checklist
from app.positioning import positioning
from app.ai_audit import quote_supported

ROOT = Path(__file__).resolve().parents[1]
GAMES = json.loads((ROOT / 'examples/fictional-games.json').read_text())


@pytest.fixture(autouse=True)
def clear_game_cache():
    # main.py caches Steam lookups for an hour; each test needs fresh mocked results.
    st.cache_data.clear()
    yield
    st.cache_data.clear()


def test_main_imports_when_run_like_streamlit_cloud(tmp_path):
    # `streamlit run app/main.py` puts app/ first on sys.path, not the repo root.
    # Running the script directly from another folder reproduces that.
    result = subprocess.run([sys.executable, str(ROOT / 'app/main.py')], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60,
                            env={**os.environ, 'OPENAI_API_KEY': ''})
    assert 'ModuleNotFoundError' not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr


def launch():
    return AppTest.from_file(str(ROOT / 'app/main.py'), default_timeout=30).run()


def submit(app, target='1', peers='2'):
    app.text_input[0].set_value(target)
    app.text_input[1].set_value(peers)
    app.button[0].click().run()
    assert not app.exception
    return app


def test_free_ui_never_calls_ai():
    with patch.dict(os.environ, {'OPENAI_API_KEY': ''}), patch('app.core.fetch_game', side_effect=GAMES), patch('app.ai_audit.ai_audit') as ai:
        app = submit(launch())
        assert any(s.value == GAMES[0]['name'] for s in app.subheader)
        assert len(app.dataframe) == 1
        assert len(app.get('download_button')) == 1
        assert any('Skipped: set OPENAI_API_KEY' in c.value for c in app.caption)
        ai.assert_not_called()


def test_failed_comparison_preserves_target_report():
    with patch.dict(os.environ, {'OPENAI_API_KEY': ''}), patch('app.core.fetch_game', side_effect=[GAMES[0], requests.ConnectionError('Fixture source unavailable')]):
        app = submit(launch())
        assert any('Comparison game 2' in w.value for w in app.warning)
        assert len(app.get('download_button')) == 1


def test_target_failure_reports_error_without_export():
    with patch.dict(os.environ, {'OPENAI_API_KEY': ''}), patch('app.core.fetch_game', side_effect=ValueError('No public fixture')):
        app = submit(launch())
        assert any('Could not analyze' in e.value for e in app.error)
        assert len(app.get('download_button')) == 0


def test_paid_ui_export_contains_successful_review():
    review = {'model': 'fixture', 'insights': [], 'dropped_insights': 0, 'disclaimer': 'Mock result'}
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'fictional-test-key'}), patch('app.core.fetch_game', side_effect=GAMES), patch('app.ai_audit.ai_audit', return_value=review), patch('streamlit.download_button', return_value=False) as download:
        app = submit(launch())
        exported = json.loads(download.call_args.args[1])
        assert exported['ai_review'] == review
        assert 'positioning' in exported
        assert 'fictional-test-key' not in json.dumps(exported)
        assert any('Model: fixture' in c.value for c in app.caption)


def test_fictional_example_reproduces_documented_output():
    expected = json.loads((ROOT / 'examples/fictional-audit.json').read_text())
    actual = audit(GAMES[0], GAMES[1:])
    actual['checklist'] = store_checklist(GAMES[0], GAMES[1:])
    actual['positioning'] = positioning(GAMES[0], GAMES[1:])
    assert actual == expected


def test_two_stitched_fragments_are_rejected():
    assert not quote_supported('Explore an orchard ... magical garden', ['explore an orchard, craft tools and grow a magical garden.'])


def test_failed_ai_keeps_free_export():
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'fictional-test-key'}), patch('app.core.fetch_game', side_effect=GAMES), patch('app.ai_audit.ai_audit', side_effect=ValueError('Fixture quote rejected')), patch('streamlit.download_button', return_value=False) as download:
        app = submit(launch())
        assert any('AI review could not be completed' in e.value for e in app.error)
        exported = json.loads(download.call_args.args[1])
        assert 'checklist' in exported and 'positioning' in exported
        assert 'ai_review' not in exported

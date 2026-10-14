import pytest
from app.core import app_id, audit

def test_app_id():
    assert app_id('1145360')==1145360
    assert app_id('https://store.steampowered.com/app/1145360/Hades/')==1145360

@pytest.mark.parametrize('bad',['https://evil.com/app/123','https://store.steampowered.com.evil.com/app/123','file:///etc/passwd','abc'])
def test_rejects_bad_input(bad):
    with pytest.raises(ValueError): app_id(bad)

def test_audit():
    game={'app_id':1,'name':'Example','short_description':'Short','screenshots':[],'genres':[]}
    result=audit(game)
    assert len(result['findings'])==3
    assert all('evidence' in f for f in result['findings'])

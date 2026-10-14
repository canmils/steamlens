import re
from urllib.parse import urlparse
import requests

STORE_API = 'https://store.steampowered.com/api/appdetails'

def app_id(value: str) -> int:
    value = value.strip()
    if re.fullmatch(r'\d{1,12}', value):
        return int(value)
    parsed = urlparse(value)
    if parsed.scheme not in ('http', 'https') or parsed.hostname not in ('store.steampowered.com',):
        raise ValueError('Enter a Steam store URL or numeric App ID.')
    match = re.match(r'^/app/(\d+)(?:/|$)', parsed.path)
    if not match:
        raise ValueError('Expected a URL like https://store.steampowered.com/app/1145360/')
    return int(match.group(1))

def fetch_game(identifier: int) -> dict:
    response = requests.get(STORE_API, params={'appids': identifier, 'cc': 'us', 'l': 'english'}, timeout=12, headers={'User-Agent':'SteamLens/0.1 (open-source research tool)'})
    response.raise_for_status()
    result = response.json().get(str(identifier), {})
    if not result.get('success') or not isinstance(result.get('data'), dict):
        raise ValueError(f'Steam did not return public store data for app {identifier}.')
    data = result['data']
    return {
        'app_id': identifier, 'name': data.get('name','Unknown'), 'type': data.get('type'),
        'short_description': data.get('short_description',''),
        'about_the_game': data.get('about_the_game',''),
        'header_image': data.get('header_image'),
        'screenshots': [s.get('path_thumbnail') for s in data.get('screenshots',[]) if s.get('path_thumbnail')],
        'genres': [g.get('description') for g in data.get('genres',[])],
        'categories': [c.get('description') for c in data.get('categories',[])],
        'developers': data.get('developers',[]),
        'release_date': data.get('release_date',{}).get('date'),
        'coming_soon': data.get('release_date',{}).get('coming_soon'),
        'price_overview': data.get('price_overview'),
        'source_url': f'https://store.steampowered.com/app/{identifier}/',
    }

def finding(code, title, severity, observation, recommendation, evidence):
    return {'id':code,'title':title,'severity':severity,'observation':observation,
            'recommendation':recommendation,'evidence':evidence,'type':'heuristic',
            'confidence':'rule-based; impact not established'}

def audit(game: dict, competitors: list[dict] | None = None) -> dict:
    findings=[]
    description=re.sub(r'<[^>]+>', '',game.get('short_description') or '').strip()
    screenshots=game.get('screenshots') or []
    genres=game.get('genres') or []
    if not description:
        findings.append(finding('missing-description','Missing short description','high',
            'No short description was returned by the public store endpoint.',
            'Check whether the store page is public and add a clear short description.',{'field':'short_description','value':description}))
    elif len(description)<80:
        findings.append(finding('short-description','Very short store description','medium',
            f'The short description contains {len(description)} characters.',
            'Review whether it communicates the game genre, main player activity and distinguishing feature.',{'field':'short_description','length':len(description)}))
    if len(screenshots)<5:
        findings.append(finding('screenshots','Limited screenshots returned','medium',
            f'The public endpoint returned {len(screenshots)} screenshots.',
            'Check the store listing and consider adding more representative gameplay screenshots.',{'field':'screenshots','count':len(screenshots)}))
    if not genres:
        findings.append(finding('genres','No genres returned','low',
            'No genre metadata was returned by the public endpoint.',
            'Review the game categorization in Steamworks.',{'field':'genres','value':genres}))
    if not findings:
        findings.append(finding('manual-review','Manual positioning review recommended','info',
            'The basic metadata checks did not flag missing or unusually short fields.',
            'Review the first screenshots, capsule and value proposition with target players. Passing these checks does not establish marketing effectiveness.',{'fields':['short_description','screenshots','genres']}))
    comparisons=[]
    for other in competitors or []:
        comparisons.append({'app_id':other['app_id'],'name':other['name'],
            'shared_genres':sorted(set(genres)&set(other.get('genres') or [])),
            'screenshot_count':len(other.get('screenshots') or []),
            'description_length':len(re.sub(r'<[^>]+>','',other.get('short_description') or '')),
            'note':'Descriptive comparison only; not a quality or conversion ranking.'})
    return {'game':game,'competitors':comparisons,'findings':findings,
            'disclaimer':'Heuristic checks only. No wishlist, sales, conversion or player estimates. Public endpoint data can be incomplete. Verify source usage terms before scaling.'}

"""Explicit network smoke check. No OpenAI calls, keys or image downloads."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core import fetch_game, audit
from app.checklist import store_checklist
from app.positioning import positioning


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Explicitly allow Steam requests')
    parser.add_argument('--output', type=Path, help='Optional JSON output, refuses to overwrite')
    args = parser.parse_args()
    if not args.live:
        parser.error('Supply --live to permit public Steam requests. Not part of offline tests.')
    games = [fetch_game(i) for i in [1145360, 1145350, 588650, 2071280]]
    result = audit(games[0], games[1:])
    result['checklist'] = store_checklist(games[0], games[1:])
    result['positioning'] = positioning(games[0], games[1:])
    result['observed_at_utc'] = datetime.now(timezone.utc).isoformat()
    assert len(result['checklist']['table']) == 4
    if args.output:
        with args.output.open('x', encoding='utf-8') as file:
            json.dump(result, file, indent=2, ensure_ascii=False)
    for game in games:
        print(f"{game['app_id']}: {game['name']} | screenshots={len(game['screenshots'])} | reviews_available={game['reviews'] is not None}")
    print('Public metadata/checklist/comparison passed. No AI or browser image rendering tested.')

if __name__ == '__main__':
    main()

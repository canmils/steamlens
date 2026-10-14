import requests
import json
import streamlit as st
from app.core import app_id, fetch_game, audit

st.set_page_config(page_title='SteamLens', page_icon='🎮', layout='wide')
st.title('🎮 SteamLens')
st.caption('Open-source Steam marketing audit · v0.1 · no AI key required')
st.info('Experimental tool: descriptive heuristics, not conversion predictions or sales estimates.')
with st.form('audit'):
    game_url=st.text_input('Steam game URL or App ID', placeholder='https://store.steampowered.com/app/1145360/')
    comps=st.text_input('Up to 3 comparison URLs or App IDs (comma-separated, optional)')
    submitted=st.form_submit_button('Analyze game', type='primary')
if submitted:
    try:
        with st.spinner('Fetching public game information...'):
            game=fetch_game(app_id(game_url))
            values=[x.strip() for x in comps.split(',') if x.strip()]
            if len(values)>3:
                st.warning('Only the first 3 comparison games will be used.')
            ids=list(dict.fromkeys(app_id(x) for x in values[:3]))
            ids=[i for i in ids if i!=game['app_id']]
            other=[]
            for i in ids:
                try: other.append(fetch_game(i))
                except (ValueError, requests.exceptions.RequestException) as exc: st.warning(f'Comparison game {i}: {exc}')
            result=audit(game,other)
        st.subheader(game['name'])
        st.markdown(f"[View original Steam listing]({game['source_url']})")
        left,right=st.columns([1,2])
        with left:
            if game.get('header_image'): st.image(game['header_image'])
        with right:
            st.write(game.get('short_description') or 'No description returned')
            st.caption('Genres: '+(', '.join(game['genres']) or 'Unavailable'))
            st.caption(f"Screenshots returned: {len(game['screenshots'])}")
        st.subheader('Audit findings')
        for f in result['findings']:
            with st.expander(f"{f['severity'].upper()} · {f['title']}",expanded=True):
                st.write('**Observation:** '+f['observation'])
                st.write('**Suggested action:** '+f['recommendation'])
                st.caption('Evidence: '+json.dumps(f['evidence'],ensure_ascii=False))
                st.caption(f['confidence'])
        if result['competitors']:
            st.subheader('Comparison games')
            st.dataframe(result['competitors'],hide_index=True,use_container_width=True)
        st.download_button('Download JSON audit',json.dumps(result,indent=2,ensure_ascii=False),file_name=f"steamlens-{game['app_id']}.json",mime='application/json')
    except (ValueError, requests.exceptions.RequestException) as exc:
        st.error(f'Could not analyze this game: {exc}')

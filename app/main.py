import json
import requests
import streamlit as st
from app.core import app_id, fetch_game, audit
from app.positioning import positioning

st.set_page_config(page_title="SteamLens", page_icon="🎮", layout="wide")
st.title("🎮 SteamLens")
st.caption("Open-source Steam marketing audit · v0.2 · no AI key required")
st.info("Evidence-based descriptive checks, not conversion predictions or sales estimates.")

with st.form("audit"):
    game_url = st.text_input("Steam game URL or App ID", placeholder="https://store.steampowered.com/app/1145360/")
    comps = st.text_input("Up to 3 comparison URLs or App IDs (comma-separated, optional)")
    submitted = st.form_submit_button("Analyze game", type="primary")

if submitted:
    try:
        with st.spinner("Fetching public game information..."):
            game = fetch_game(app_id(game_url))
            values = [x.strip() for x in comps.split(",") if x.strip()]
            if len(values) > 3:
                st.warning("Only the first 3 comparison games will be used.")
            ids = list(dict.fromkeys(app_id(x) for x in values[:3]))
            others = []
            for identifier in ids:
                if identifier == game["app_id"]:
                    continue
                try:
                    others.append(fetch_game(identifier))
                except (ValueError, requests.exceptions.RequestException) as exc:
                    st.warning(f"Comparison game {identifier}: {exc}")
            result = audit(game, others)
        st.subheader(game["name"])
        st.markdown(f"[View original Steam listing]({game['source_url']})")
        left, right = st.columns([1, 2])
        with left:
            if game.get("header_image"):
                st.image(game["header_image"], use_container_width=True)
        with right:
            st.write(game.get("short_description") or "No description returned")
            st.caption("Genres: " + (", ".join(game["genres"]) or "Unavailable"))
            st.caption("Categories: " + (", ".join(game["categories"]) or "Unavailable"))
            st.caption(f"Screenshots returned: {len(game['screenshots'])}")
        if game["screenshots"]:
            st.subheader("First five screenshots")
            columns = st.columns(min(5, len(game["screenshots"])))
            for idx, screenshot in enumerate(game["screenshots"][:5]):
                columns[idx].image(screenshot, use_container_width=True, caption=f"#{idx + 1}")
        st.subheader("Audit findings")
        for item in result["findings"]:
            with st.expander(f"{item['severity'].upper()} · {item['title']}", expanded=True):
                st.write("**Observation:** " + item["observation"])
                st.write("**Suggested action:** " + item["recommendation"])
                st.caption("Evidence: " + ", ".join(item["evidence"].get("names", []))
                           if item["id"] == "comparison-review"
                           else "Evidence field: " + item["evidence"].get("field", "public metadata"))
                st.caption(item["confidence"])
        if result["competitors"]:
            st.subheader("Competitor comparison")
            st.caption("Selected by you; similarity and marketing performance are not inferred.")
            rows = [{
                "Game": game["name"], "Genres": ", ".join(game["genres"]),
                "Description characters": len(game.get("short_description") or ""),
                "Screenshots": len(game["screenshots"])
            }]
            for item in result["competitors"]:
                rows.append({
                    "Game": item["name"], "Genres": ", ".join(item["genres"]),
                    "Description characters": item["description_length"],
                    "Screenshots": item["screenshot_count"]
                })
            st.dataframe(rows, hide_index=True, use_container_width=True)
            for item in result["competitors"]:
                with st.expander(f"Positioning: {item['name']}"):
                    st.write(item["short_description"] or "No description returned")
                    st.caption("Shared genres: " + (", ".join(item["shared_genres"]) or "None returned"))
                    if item["source_url"]:
                        st.markdown(f"[View Steam listing]({item['source_url']})")
        if others:
            st.subheader("Positioning signals (experimental)")
            st.caption("Exact phrases found in public short descriptions. These are not AI judgments or quality scores.")
            report = positioning(game, others)
            for entry in report["games"]:
                with st.expander(entry["name"] + " — positioning evidence", expanded=True):
                    if entry["signals"]:
                        for label, phrases in entry["signals"].items():
                            st.write("**" + label + ":** " + ", ".join(phrases))
                    else:
                        st.write("No configured keyword signals detected.")
            st.write("**Signals in Hades and at least one competitor:** " + (", ".join(report["shared"]) or "None detected"))
            st.write("**Signals detected only in the target description:** " + (", ".join(report["main_only"]) or "None detected"))
            st.write("**Signals detected only in competitor descriptions:** " + (", ".join(report["peer_only"]) or "None detected"))
            st.info("Research prompt: Which detected positioning differences are meaningful to your audience? Verify against actual gameplay and visuals.")
            st.caption(report["method"])
        st.caption(result["disclaimer"])
        st.download_button("Download JSON audit", json.dumps(result, indent=2, ensure_ascii=False),
                           file_name=f"steamlens-{game['app_id']}.json", mime="application/json")
    except (ValueError, requests.exceptions.RequestException) as exc:
        st.error(f"Could not analyze this game: {exc}")

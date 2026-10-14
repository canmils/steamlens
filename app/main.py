import json
import os
import requests
import streamlit as st
from app.core import app_id, fetch_game, audit
from app.positioning import positioning
from app.ai_audit import ai_audit
from app.checklist import store_checklist
from openai import OpenAIError

st.set_page_config(page_title="SteamLens", page_icon="🎮", layout="wide")
st.title("🎮 SteamLens")
st.caption("Open-source Steam store page audit · v0.5.1 beta")
st.info("Compare your Steam store page with up to 3 games you choose. The checklist is free and needs no API key. "
        "The optional AI review needs your own OpenAI API key, may incur charges and sends public game text to OpenAI.")
api_key = os.getenv("OPENAI_API_KEY", "").strip()
if not api_key:
    st.caption("No OPENAI_API_KEY set: the checklist and comparison work; the AI review is skipped.")

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
                st.image(game["header_image"], width='stretch')
        with right:
            st.write(game.get("short_description") or "No description returned")
            st.caption("Genres: " + (", ".join(game["genres"]) or "Unavailable"))
            st.caption("Categories: " + (", ".join(game["categories"]) or "Unavailable"))
            st.caption(f"Screenshots returned: {len(game['screenshots'])}")
        if game["screenshots"]:
            st.subheader("First five screenshots")
            columns = st.columns(min(5, len(game["screenshots"])))
            for idx, screenshot in enumerate(game["screenshots"][:5]):
                columns[idx].image(screenshot, width='stretch', caption=f"#{idx + 1}")
        report_checks = store_checklist(game, others)
        result["checklist"] = report_checks
        st.subheader("Store page checklist")
        icons = {"ok": "\u2705", "review": "\U0001F7E1", "missing": "\u274C"}
        for item in report_checks["checks"]:
            line = f"{icons[item['status']]} **{item['check']}:** {item['detail']}"
            if item["action"]:
                line += f"  \n{item['action']}"
            st.markdown(line)
        st.caption(report_checks["note"])
        st.subheader("Side-by-side comparison" if others else "Store page numbers")
        labels = {"name": "Game", "short_description_chars": "Short description (chars)", "about_words": "About text (words)",
                  "screenshots": "Screenshots", "trailers": "Trailers", "languages": "Languages",
                  "full_audio_languages": "Full audio languages", "platforms": "Platforms",
                  "controller_support": "Controller", "achievements": "Achievements", "price": "Price (US)",
                  "reviews_total": "Reviews", "reviews_positive_pct": "% positive", "release": "Release"}
        st.dataframe([{labels[k]: v for k, v in row.items() if k in labels} for row in report_checks["table"]],
                     hide_index=True, width='stretch')
        if result["competitors"]:
            st.subheader("Competitor descriptions")
            st.caption("Selected by you; similarity and marketing performance are not inferred.")
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
            st.write("**Signals in the target and at least one competitor:** " + (", ".join(report["shared"]) or "None detected"))
            st.write("**Signals detected only in the target description:** " + (", ".join(report["main_only"]) or "None detected"))
            st.write("**Signals detected only in competitor descriptions:** " + (", ".join(report["peer_only"]) or "None detected"))
            st.info("Research prompt: Which detected positioning differences are meaningful to your audience? Verify against actual gameplay and visuals.")
            st.caption(report["method"])
        st.subheader("AI positioning review (optional)")
        ai_result = None
        if not api_key:
            st.caption("Skipped: set OPENAI_API_KEY before starting SteamLens to enable it.")
        elif not others:
            st.caption("Skipped: add at least one comparison game. The AI review compares your text with theirs.")
        else:
            with st.spinner("Generating evidence-backed positioning observations..."):
                try:
                    ai_result = ai_audit(game, others, api_key)
                except (OpenAIError, ValueError) as exc:
                    st.error("AI review could not be completed (" + type(exc).__name__ + ").")
                    if isinstance(exc, ValueError):
                        st.caption("Reason: " + str(exc))
                    else:
                        st.caption("OpenAI request failed. Check API billing, model access, and connectivity.")
        if ai_result:
            st.caption("Model: " + ai_result["model"] + " \u00b7 AI-generated hypotheses, not proven results")
            for insight in ai_result["insights"]:
                with st.container(border=True):
                    st.markdown("**" + insight["title"] + "**")
                    st.write(insight["interpretation"])
                    st.write("**Suggested experiment:** " + insight["action"])
                    st.caption("Matched store-text evidence (App " + insight["evidence_app_id"] + "): \u201c" + insight["evidence_quote"] + "\u201d")
            if ai_result.get("dropped_insights"):
                st.caption(f"{ai_result['dropped_insights']} AI insight(s) hidden: evidence quote did not match the source text.")
            st.caption(ai_result["disclaimer"])
        st.caption(result["disclaimer"])
        if ai_result is not None:
            result["ai_review"] = ai_result
        st.download_button("Download JSON audit", json.dumps(result, indent=2, ensure_ascii=False),
                           file_name=f"steamlens-{game['app_id']}.json", mime="application/json")
    except (ValueError, requests.exceptions.RequestException) as exc:
        st.error(f"Could not analyze this game: {exc}")

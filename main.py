import html
import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import altair as alt
import pandas as pd
import streamlit as st
from matching import MAX_SCORE, analyze_opportunities, cost_label

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "opportunities.json"
SUBJECTS = ["Computer Science", "Math", "Science", "Engineering", "Physics"]
TYPES = ["Any", "Competition", "Summer Program", "Internship", "Research", "Scholarship", "Hackathon"]
FORMATS = ["Both", "Online", "Onsite"]
TODAY = datetime.now(ZoneInfo("America/New_York")).date()

st.set_page_config(page_title="Jumpad | STEM Opportunities", page_icon="✦", layout="wide")

# A warm editorial visual system with a deep green navigation rail. The UI uses
# ordinary Streamlit components, so all existing controls retain their behavior.
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --ink: #12332c;
  --ink-2: #245248;
  --muted: #66746e;
  --paper: #f7f3eb;
  --paper-2: #fffdf8;
  --line: #ded7ca;
  --mint: #d9eee4;
  --aqua: #43ad91;
  --coral: #e86848;
  --coral-deep: #b84c34;
  --sun: #f5bf48;
  --shadow: 0 14px 36px rgba(19, 48, 42, .09);
  --radius: 18px;
}

* { box-sizing: border-box; }
.stApp {
  color: var(--ink);
  font-family: "Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif;
  background:
    radial-gradient(circle at 88% 2%, rgba(210, 236, 219, .92) 0, rgba(210, 236, 219, 0) 24rem),
    radial-gradient(circle at 52% 98%, rgba(255, 222, 173, .34) 0, rgba(255, 222, 173, 0) 29rem),
    var(--paper);
}
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1370px; padding: 1.45rem 2rem 4rem; }

/* Sidebar */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
  background: linear-gradient(168deg, #10362f 0%, #0a2520 100%);
}
[data-testid="stSidebar"] { border-right: 0; }
[data-testid="stSidebar"] .block-container { padding: 1.35rem 1rem 2.2rem; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: rgba(240, 247, 240, .68); }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label { color: #f8f5eb; font-size: .83rem; font-weight: 700; letter-spacing: .01em; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] label { color: rgba(250, 250, 244, .91) !important; font-size: .87rem; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] [data-testid="stCheckbox"] { accent-color: var(--sun); }
.sidebar-brand { display: flex; gap: 11px; align-items: center; margin: .05rem 0 2rem; }
.brand-mark { display: grid; place-items: center; width: 38px; height: 38px; border-radius: 13px; background: var(--sun); color: #11342d; font-family: "DM Serif Display", Georgia, serif; font-size: 1.35rem; font-weight: 700; transform: rotate(-7deg); }
.brand-copy { display: flex; flex-direction: column; gap: 1px; }
.brand-copy b { color: #fffdf6; font-size: 1rem; letter-spacing: .08em; }
.brand-copy span { color: #a9c9bc; font-size: .72rem; font-weight: 600; }
.side-eyebrow { margin: 0 0 .2rem; color: #a9c9bc; font-size: .7rem; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; }
.side-heading { margin: 0 0 .85rem; color: #fffdf7; font-family: "DM Serif Display", Georgia, serif; font-size: 1.3rem; line-height: 1.1; }
.sidebar-divider { height: 1px; margin: 1.35rem 0; background: rgba(214, 238, 225, .18); }
[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stSlider"] > div > div {
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  background: rgba(255, 255, 255, .08) !important;
  border: 1px solid rgba(220, 242, 230, .24) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  color: #fffdf7 !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder { color: rgba(240, 247, 240, .45); }
/* Keep the interest picker fully opaque and make its menu affordance easy to spot. */
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  background: #214b40 !important;
  border-color: #91b9a7 !important;
}
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"]:hover > div,
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"]:focus-within > div {
  border-color: #f5bf48 !important;
  box-shadow: 0 0 0 3px rgba(245, 191, 72, .2) !important;
}
[data-testid="stSidebar"] [data-testid="stMultiSelect"] svg {
  opacity: 1 !important;
  color: #f5bf48 !important;
  fill: #f5bf48 !important;
  stroke: #f5bf48 !important;
}
.interest-picker-cue {
  display: inline-flex; align-items: center; gap: 7px;
  margin: 0 0 7px; padding: 5px 9px; border-radius: 8px;
  background: #f5bf48; color: #17382f; font-size: .72rem;
  font-weight: 800; letter-spacing: .04em; text-transform: uppercase;
}
.interest-picker-cue span { font-size: 1rem; line-height: .8; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg,
[data-testid="stSidebar"] [data-testid="stMultiSelect"] svg { color: #fffdf7 !important; fill: #fffdf7 !important; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg { color: #fffdf7 !important; fill: #fffdf7 !important; }
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within { border-color: var(--sun) !important; box-shadow: 0 0 0 3px rgba(245, 191, 72, .16) !important; }
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] { background: var(--sun); border-color: var(--sun); }
[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBar"],
[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stThumbValue"] { color: #d8eadf; }
/* A distinct budget control that stays visible against either app theme. */
[data-testid="stSidebar"] .st-key-budget {
  margin: 5px 0 0; padding: 12px 12px 7px;
  border: 1px solid #568875; border-radius: 14px;
  background: #153d34 !important;
  box-shadow: inset 0 0 0 1px rgba(245, 191, 72, .12);
}
[data-testid="stSidebar"] .st-key-budget [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] .st-key-budget [data-testid="stWidgetLabel"] label {
  color: #fffdf7 !important; font-size: .9rem; font-weight: 800;
}
[data-testid="stSidebar"] .st-key-budget [data-baseweb="slider"] [role="slider"] {
  width: 25px !important; height: 25px !important;
  background: #ffd15d !important; border: 3px solid #102c25 !important;
  box-shadow: 0 0 0 3px #ffd15d, 0 2px 8px rgba(0, 0, 0, .45) !important;
  opacity: 1 !important; cursor: grab;
}
[data-testid="stSidebar"] .st-key-budget [data-baseweb="slider"] [role="slider"]:active { cursor: grabbing; }
[data-testid="stSidebar"] .st-key-budget [data-baseweb="slider"] > div > div {
  background-color: #91b9a7 !important; opacity: 1 !important;
}
[data-testid="stSidebar"] .st-key-budget [data-baseweb="slider"] > div > div[style*="width"] {
  background-color: #ffd15d !important;
}
[data-testid="stSidebar"] .st-key-budget [data-testid="stTickBar"],
[data-testid="stSidebar"] .st-key-budget [data-testid="stThumbValue"] { color: #fff4cf !important; opacity: 1 !important; }
[data-testid="stSidebar"] .st-key-budget:focus-within {
  outline: 3px solid #ffd15d; outline-offset: 3px; border-color: #ffd15d;
}
.sidebar-budget { margin: 7px 0 5px; color: #d9e9df; font-size: .78rem; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] [data-testid="stMarkdownContainer"] p { color: #eef6f0 !important; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] > label > span:first-child { border-color: rgba(235, 249, 240, .55); }

/* Streamlit controls */
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"] > div, [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  min-height: 42px; border: 1px solid var(--line) !important; border-radius: 12px !important; background: var(--paper-2) !important; color: var(--ink) !important; box-shadow: none !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within, [data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within { border-color: var(--aqua) !important; box-shadow: 0 0 0 3px rgba(67, 173, 145, .14) !important; }
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label { color: var(--ink); font-size: .84rem; font-weight: 700; }
[data-baseweb="popover"], [data-baseweb="menu"] { background: #fffdf8 !important; }
[data-baseweb="menu"] li { color: var(--ink) !important; }
[data-testid="stButton"] button {
  min-height: 39px; border: 1px solid var(--line) !important; border-radius: 11px !important; background: var(--paper-2) !important; color: var(--ink) !important; box-shadow: none !important; font-weight: 700; transition: transform .16s ease, border-color .16s ease, background .16s ease;
}
[data-testid="stButton"] button:hover { transform: translateY(-1px); border-color: var(--aqua) !important; background: #f1faf5 !important; color: var(--ink) !important; }
[data-testid="stLinkButton"] a { min-height: 42px; border: 1px solid var(--ink) !important; border-radius: 11px !important; background: var(--ink) !important; color: #fffdf7 !important; font-weight: 700; transition: transform .16s ease, background .16s ease; }
[data-testid="stLinkButton"] a:hover { transform: translateY(-1px); background: var(--ink-2) !important; border-color: var(--ink-2) !important; }
[data-testid="stExpander"] { border: 1px solid #e6dfd4 !important; border-radius: 12px !important; background: #fbfaf6 !important; }
[data-testid="stExpander"] summary { color: var(--ink); font-weight: 700; }
[data-testid="stCheckbox"] label { min-height: 36px; }

/* Sidebar actions */
.st-key-filter-links button, .st-key-reset-button button { min-height: 31px; padding: 2px 5px; border: 0 !important; border-radius: 8px !important; background: transparent !important; color: #bce0ce !important; font-size: .77rem; font-weight: 600; text-decoration: underline; text-underline-offset: 3px; }
.st-key-filter-links button:hover, .st-key-reset-button button:hover { transform: none; background: rgba(255,255,255,.08) !important; color: #fffdf7 !important; }
.sidebar-budget { margin: -2px 0 5px; color: #b7d2c3; font-size: .75rem; }
.sidebar-budget strong { color: var(--sun); }

/* Hero */
.hero { position: relative; display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(260px, .8fr); gap: 2rem; align-items: stretch; overflow: hidden; min-height: 237px; padding: 2.2rem 2.4rem; border: 1px solid rgba(29, 81, 69, .15); border-radius: 26px; background: linear-gradient(118deg, #19483e 0%, #174139 58%, #276357 100%); box-shadow: 0 15px 34px rgba(19, 48, 42, .13); }
.hero::before { content: ""; position: absolute; right: 19%; bottom: -115px; width: 240px; height: 240px; border: 1px solid rgba(239, 250, 242, .16); border-radius: 50%; box-shadow: 0 0 0 31px rgba(239, 250, 242, .05), 0 0 0 65px rgba(239, 250, 242, .04); }
.hero::after { content: ""; position: absolute; width: 16px; height: 16px; left: 48%; top: 24px; border-radius: 50%; background: var(--sun); box-shadow: 187px 72px 0 -4px var(--coral), 241px -8px 0 -6px #b8e4d3; opacity: .98; }
.hero-copy, .hero-summary { position: relative; z-index: 1; }
.hero-copy { max-width: 700px; }
.hero-kicker { display: flex; align-items: center; gap: 8px; color: #bce2d0; font-size: .74rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
.hero-kicker::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--sun); box-shadow: 0 0 0 4px rgba(245, 191, 72, .15); }
.hero h1 { margin: .66rem 0 .55rem; color: #fffdf6; font-family: "DM Serif Display", Georgia, serif; font-size: clamp(2.35rem, 4vw, 4.1rem); font-weight: 400; letter-spacing: -.045em; line-height: .96; }
.hero h1 em { color: #bce9d7; font-style: italic; }
.hero p { max-width: 540px; margin: 0; color: #c6ddd3; font-size: 1rem; line-height: 1.52; }
.hero-summary { display: flex; align-items: flex-end; justify-content: flex-end; }
.hero-count { width: min(100%, 235px); padding: 1.2rem 1.25rem; border: 1px solid rgba(246, 253, 248, .2); border-radius: 18px; background: rgba(10, 37, 32, .28); backdrop-filter: blur(5px); }
.hero-count strong { display: block; color: var(--sun); font-family: "DM Serif Display", Georgia, serif; font-size: 3.05rem; line-height: .95; letter-spacing: -.055em; }
.hero-count span { display: block; margin-top: .5rem; color: #e0ede5; font-size: .8rem; font-weight: 600; line-height: 1.35; }

/* Results shell */
.results-toolbar { display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin: 1.65rem 0 .55rem; }
.results-label { margin: 0 0 .18rem; color: var(--aqua); font-size: .73rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
.results-title { margin: 0; color: var(--ink); font-family: "DM Serif Display", Georgia, serif; font-size: 1.72rem; font-weight: 400; letter-spacing: -.025em; }
.result-stat { display: flex; align-items: center; gap: .55rem; margin: 0 0 1rem; color: var(--muted); font-size: .9rem; }
.result-stat::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--aqua); box-shadow: 0 0 0 4px rgba(67, 173, 145, .12); }
.result-stat strong { color: var(--ink); font-weight: 700; }
.sort-wrap { min-width: 210px; }
.sort-wrap [data-testid="stSelectbox"] > div > div { min-height: 40px; }
.saved-toggle [data-testid="stCheckbox"] { margin-top: .35rem; }
.saved-toggle [data-testid="stCheckbox"] label { color: var(--ink); font-weight: 700; }

/* Opportunity cards */
[class*="st-key-opportunity-list"] [data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid rgba(25, 72, 62, .14) !important; border-radius: var(--radius) !important; background: rgba(255, 253, 248, .94) !important; box-shadow: 0 8px 24px rgba(30, 56, 49, .055); transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease; }
[class*="st-key-opportunity-list"] [data-testid="stVerticalBlockBorderWrapper"]:hover { transform: translateY(-3px); border-color: rgba(67, 173, 145, .62) !important; box-shadow: var(--shadow); }
.opportunity-title { color: var(--ink); font-family: "DM Serif Display", Georgia, serif; font-size: 1.34rem; font-weight: 400; letter-spacing: -.015em; line-height: 1.2; text-decoration: none; }
.opportunity-title:hover { color: var(--coral-deep); text-decoration: underline; text-decoration-color: rgba(232, 104, 72, .5); text-underline-offset: 4px; }
.match-badge { display: inline-flex; align-items: center; justify-content: center; min-height: 38px; padding: 7px 10px; border: 1px solid #ded9ce; border-radius: 999px; background: #f4f0e9; color: #405750; font-size: .77rem; font-weight: 700; white-space: nowrap; }
.match-badge.strong { border-color: #a5d6c4; background: #e7f5ed; color: #236550; }
.match-badge.good { border-color: #f1d498; background: #fff3d9; color: #805613; }
.match-badge.partial { border-color: #e5cdc0; background: #fff0e9; color: #9b4b36; }
.chip-row { display: flex; align-items: center; flex-wrap: wrap; gap: 7px; margin: 9px 0 11px; }
.tag { display: inline-flex; align-items: center; min-height: 25px; padding: 4px 9px; border-radius: 999px; font-size: .72rem; font-weight: 700; letter-spacing: .01em; }
.tag.type { background: #e6f3ec; color: #28634f; }
.tag.format { background: #eaf0f4; color: #365566; }
.tag.free { background: #e4f4e9; color: #24704f; }
.desc-clamp { display: -webkit-box; min-height: 2.75em; margin: 4px 0 15px; overflow: hidden; color: #53635d; font-size: .9rem; line-height: 1.5; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.metadata { display: grid; grid-template-columns: 1.3fr .95fr 1.25fr .8fr 1.25fr; gap: 12px; padding: 13px 0; border-top: 1px solid #ebe5db; border-bottom: 1px solid #ebe5db; }
.meta-item { min-width: 0; }
.meta-label { margin-bottom: 4px; color: #8a9690; font-size: .69rem; font-weight: 700; letter-spacing: .075em; text-transform: uppercase; }
.meta-value { color: #28423a; font-size: .86rem; font-weight: 600; line-height: 1.42; overflow-wrap: anywhere; }
.deadline .meta-value { font-weight: 700; }
.deadline.soon .meta-value, .deadline.closed .meta-value { color: var(--coral-deep); }
.why-line { margin: 11px 0 6px; color: #4f5f58; font-size: .85rem; line-height: 1.45; }
.why-line strong { color: var(--ink); }

/* Discovery helpers */
.closing-strip { position: relative; overflow: hidden; padding: 13px 15px; margin: 0 0 14px; border: 1px solid #f0d49b; border-radius: 14px; background: linear-gradient(100deg, #fff7e7, #fffdf8); }
.closing-strip::after { content: ""; position: absolute; right: 18px; top: -22px; width: 80px; height: 80px; border: 12px solid rgba(245, 191, 72, .18); border-radius: 50%; }
.closing-title { position: relative; z-index: 1; margin: 0 0 6px; color: #795313; font-size: .78rem; font-weight: 800; letter-spacing: .09em; text-transform: uppercase; }
.closing-items { position: relative; z-index: 1; display: flex; flex-wrap: wrap; gap: 7px 18px; color: #765f3a; font-size: .84rem; }
.closing-items a { color: #775015; font-weight: 700; text-decoration: none; border-bottom: 1px solid rgba(119, 80, 21, .35); }
.closing-items a:hover { color: var(--coral-deep); }
.filter-explainer { margin: 7px 0; color: var(--muted); font-size: .85rem; line-height: 1.45; }
.compact-note { color: var(--muted); font-size: .82rem; line-height: 1.42; }
.section-title { margin: 1.8rem 0 .7rem; color: var(--ink); font-family: "DM Serif Display", Georgia, serif; font-size: 1.55rem !important; font-weight: 400; letter-spacing: -.015em; }
.analytics-shell { margin: 1.5rem 0 1.35rem; padding: 1.05rem 1.1rem 1.2rem; border: 1px solid rgba(25, 72, 62, .13); border-radius: 18px; background: rgba(255, 253, 248, .72); box-shadow: 0 8px 22px rgba(30, 56, 49, .045); }
.analytics-heading { display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin-bottom: .75rem; }
.analytics-kicker { margin: 0 0 .18rem; color: var(--aqua); font-size: .68rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
.analytics-title { margin: 0; color: var(--ink); font-family: "DM Serif Display", Georgia, serif; font-size: 1.45rem; font-weight: 400; letter-spacing: -.015em; }
.analytics-note { margin: 0; color: var(--muted); font-size: .75rem; text-align: right; }
.stat-tile { min-height: 78px; padding: .72rem .85rem; border: 1px solid #e5ded2; border-radius: 13px; background: #fffdf8; }
.stat-label { color: #83908a; font-size: .67rem; font-weight: 800; letter-spacing: .09em; text-transform: uppercase; }
.stat-value { margin-top: .22rem; color: var(--ink); font-family: "DM Serif Display", Georgia, serif; font-size: 1.7rem; line-height: 1; }
.stat-hint { margin-top: .25rem; color: var(--muted); font-size: .68rem; }
.st-key-relaxers { margin-top: 1.1rem; padding: 1rem 1.1rem; border: 1px dashed #c9d7cf; border-radius: 15px; background: rgba(255, 253, 248, .55); }
.st-key-relaxers [data-testid="stButton"] button { min-height: 38px; border: 1px solid #b9d9ca !important; border-radius: 999px !important; background: #f0faf4 !important; color: #245d4c !important; font-size: .8rem; }
.st-key-relaxers [data-testid="stButton"] button:hover { background: #e2f4ea !important; border-color: var(--aqua) !important; }

@media (max-width: 900px) {
  .block-container { padding: 1rem 1rem 3rem; }
  .hero { grid-template-columns: 1fr; min-height: 0; padding: 1.8rem; }
  .hero-summary { justify-content: flex-start; }
  .hero-count { width: 210px; }
  .metadata { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .hero { border-radius: 20px; }
  .hero h1 { font-size: 2.5rem; }
  .results-toolbar { align-items: stretch; flex-direction: column; }
  .sort-wrap { min-width: 100%; }
  .metadata { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
  [class*="st-key-opportunity-list"] [data-testid="stHorizontalBlock"] { gap: .45rem; }
  [class*="st-key-opportunity-list"] [data-testid="stButton"] button { min-height: 42px; font-size: .78rem; }
}
</style>
""",
    unsafe_allow_html=True,
)


def load_opportunities():
    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Opportunity data file not found: {DATA_FILE.name}") from exc
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"Could not read {DATA_FILE.name}: {exc}") from exc
    if not isinstance(data, list):
        raise RuntimeError("The opportunity data must be a JSON list.")
    return data


def safe(value):
    return html.escape(str(value), quote=True)


def reset_filters():
    defaults = {
        "profile_name": "", "profile_grade": 9, "selected_subjects": ["Computer Science"],
        "preferred_format": "Both", "chosen_type": "Any", "budget": 500,
        "free_only": False, "include_saved_only": False, "sort_order": "Best match",
        "relax_budget": False, "relax_type": False, "relax_deadline": False,
    }
    for key, value in defaults.items():
        st.session_state[key] = value
    for subject in SUBJECTS:
        st.session_state[subject_key(subject)] = subject == "Computer Science"


def subject_key(subject):
    return "interest_" + "_".join(subject.lower().split())


def set_all_subjects(value):
    st.session_state["selected_subjects"] = SUBJECTS.copy() if value else []
    for subject in SUBJECTS:
        st.session_state[subject_key(subject)] = value


def relative_deadline(deadline):
    days = (deadline - TODAY).days
    if days < 0:
        return "Closed", "closed"
    if days == 0:
        return "Closes today", "soon"
    if days == 1:
        return "Closes in 1 day", "soon"
    cue = f"Closes in {days} days"
    return cue, "soon" if days < 14 else ""


def match_label(score):
    # Thresholds: 5 = Strong, 3–4 = Good, and 0–2 = Partial against the 5-point scale.
    if score >= 5:
        return "Strong match", "strong"
    if score >= 3:
        return "Good match", "good"
    return "Partial match", "partial"


def render_card(opp, card_index, saved_names):
    name = opp["name"]
    key = f"save_{card_index}_{abs(hash(name))}"
    is_saved = name in saved_names
    badge, badge_class = match_label(opp["score"])
    badge_detail = f"{opp['score']} of {MAX_SCORE} match points"
    relative, deadline_class = relative_deadline(opp["deadline"])
    deadline_date = opp["deadline"].strftime("%b %d, %Y")
    price = cost_label(opp)
    free = opp.get("cost_known") and opp.get("cost") == 0
    with st.container(border=True, key=f"opportunity-list-{card_index}"):
        title_col, badge_col, save_col = st.columns([6.4, 1.7, 1.1])
        with title_col:
            st.markdown(
                f'<a class="opportunity-title" href="{safe(opp["link"])}" target="_blank" rel="noopener noreferrer">{safe(name)} ↗</a>',
                unsafe_allow_html=True,
            )
        with badge_col:
            st.markdown(
                f'<span class="match-badge {badge_class}" title="{safe(badge_detail)}">{badge}</span>',
                unsafe_allow_html=True,
            )
        with save_col:
            if st.button(
                "★ Saved" if is_saved else "☆ Save",
                key=key,
                help="Save this opportunity" if not is_saved else "Remove from saved opportunities",
            ):
                updated = set(st.session_state.get("saved_opportunities", []))
                if name in updated:
                    updated.remove(name)
                else:
                    updated.add(name)
                st.session_state["saved_opportunities"] = sorted(updated)
                st.rerun()

        st.markdown(
            f'<div class="chip-row"><span class="tag type">{safe(opp["type"])}</span><span class="tag format">{safe(opp["format"])}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="desc-clamp">{safe(opp["description"])}</div>', unsafe_allow_html=True)
        subjects = ", ".join(opp["subjects"]) or "General"
        cost_display = '<span class="tag free">Free</span>' if free else safe(price)
        deadline_markup = (
            f'<div class="meta-item deadline {deadline_class}"><div class="meta-label">Deadline</div>'
            f'<div class="meta-value">{safe(deadline_date)}<br>{safe(relative)}</div></div>'
        )
        st.markdown(
            f"""
            <div class="metadata">
              <div class="meta-item"><div class="meta-label">Subject</div><div class="meta-value">{safe(subjects)}</div></div>
              <div class="meta-item"><div class="meta-label">Minimum grade</div><div class="meta-value">{safe(opp['grade_label'])}</div></div>
              <div class="meta-item"><div class="meta-label">Location</div><div class="meta-value">{safe(opp['location'])}</div></div>
              <div class="meta-item"><div class="meta-label">Cost</div><div class="meta-value">{cost_display}</div></div>
              {deadline_markup}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="why-line"><strong>Why it matches:</strong> {safe(" ".join(opp["reasons"]))}</div>',
            unsafe_allow_html=True,
        )
        with st.expander("See eligibility details", expanded=False):
            for check in opp["eligibility_checks"]:
                if opp["deadline"] < TODAY and check.startswith("Deadline ("):
                    check = (
                        f"Deadline ({opp['deadline'].isoformat()}) has passed; this listing is shown because closed listings "
                        "are included. Check the organizer for a new cycle."
                    )
                st.markdown(f"- {safe(check)}")
        st.link_button("View details", opp["link"])
        st.caption(badge_detail)


def render_analytics(opportunities, results, filter_counts):
    """Render interactive charts from the live opportunity directory and filters."""
    if results:
        score_rows = []
        for score in range(MAX_SCORE + 1):
            label = match_label(score)[0]
            score_rows.append({"Match level": label, "Opportunities": sum(opp.get("score", 0) == score for opp in results)})
        type_rows = (
            pd.Series([opp.get("type", "Other") for opp in results], dtype="string")
            .value_counts()
            .rename_axis("Opportunity type")
            .reset_index(name="Opportunities")
        )
        format_rows = (
            pd.Series([opp.get("format", "Other") for opp in results], dtype="string")
            .value_counts()
            .rename_axis("Format")
            .reset_index(name="Opportunities")
        )
        deadline_rows = pd.DataFrame(
            {
                "Deadline status": ["Open", "Closing in 14 days", "Past deadline"],
                "Opportunities": [
                    sum((opp["deadline"] - TODAY).days >= 14 for opp in results),
                    sum(0 <= (opp["deadline"] - TODAY).days < 14 for opp in results),
                    sum((opp["deadline"] - TODAY).days < 0 for opp in results),
                ],
            }
        )
    else:
        score_rows = [{"Match level": match_label(score)[0], "Opportunities": 0} for score in range(MAX_SCORE + 1)]
        type_rows = pd.DataFrame({"Opportunity type": ["No matches"], "Opportunities": [0]})
        format_rows = pd.DataFrame({"Format": ["No matches"], "Opportunities": [0]})
        deadline_rows = pd.DataFrame({"Deadline status": ["No matches"], "Opportunities": [0]})

    score_df = pd.DataFrame(score_rows)
    average_score = (sum(opp.get("score", 0) for opp in results) / len(results)) if results else 0
    strong_count = sum(opp.get("score", 0) >= 5 for opp in results)
    free_count = sum(opp.get("cost_known") and opp.get("cost") == 0 for opp in results)
    excluded_rows = pd.DataFrame(
        {
            "Filter signal": ["Over budget", "Different type", "Past deadline", "Below grade"],
            "Listings": [
                filter_counts["over_budget"],
                filter_counts["different_type"],
                filter_counts["deadline_passed"],
                filter_counts["below_grade"],
            ],
        }
    )

    st.markdown(
        '<section class="analytics-shell"><div class="analytics-heading"><div><p class="analytics-kicker">Live search intelligence</p><h2 class="analytics-title">See what is shaping your shortlist</h2></div><p class="analytics-note">Charts update with your filters · hover to inspect</p></div>',
        unsafe_allow_html=True,
    )
    stat_cols = st.columns(4)
    stat_data = [
        ("Average match", f"{average_score:.1f}/{MAX_SCORE}", "across current results"),
        ("Strong matches", str(strong_count), "5-point matches"),
        ("Free options", str(free_count), "no listed individual cost"),
        ("Directory size", str(len(opportunities)), "total listings indexed"),
    ]
    for col, (label, value, hint) in zip(stat_cols, stat_data):
        with col:
            st.markdown(
                f'<div class="stat-tile"><div class="stat-label">{label}</div><div class="stat-value">{value}</div><div class="stat-hint">{hint}</div></div>',
                unsafe_allow_html=True,
            )

    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.markdown("**Match strength**")
        score_chart = (
            alt.Chart(score_df)
            .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, color="#43ad91")
            .encode(
                x=alt.X("Match level:N", sort=["Strong match", "Good match", "Partial match"], title=None),
                y=alt.Y("Opportunities:Q", title="Listings", scale=alt.Scale(domain=[0, max(1, int(score_df["Opportunities"].max()))])),
                tooltip=[alt.Tooltip("Match level:N", title="Match"), alt.Tooltip("Opportunities:Q", title="Listings")],
            )
            .properties(height=215)
            .interactive()
        )
        st.altair_chart(score_chart, use_container_width=True)
    with chart_cols[1]:
        st.markdown("**Opportunity mix**")
        type_chart = (
            alt.Chart(type_rows)
            .mark_bar(cornerRadiusEnd=5, color="#e86848")
            .encode(
                y=alt.Y("Opportunity type:N", sort="-x", title=None),
                x=alt.X("Opportunities:Q", title="Listings"),
                tooltip=[alt.Tooltip("Opportunity type:N", title="Type"), alt.Tooltip("Opportunities:Q", title="Listings")],
            )
            .properties(height=215)
            .interactive()
        )
        st.altair_chart(type_chart, use_container_width=True)

    detail_cols = st.columns(2)
    with detail_cols[0]:
        st.markdown("**Deadline pulse**")
        deadline_chart = (
            alt.Chart(deadline_rows)
            .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, color="#f5bf48")
            .encode(
                x=alt.X("Deadline status:N", title=None),
                y=alt.Y("Opportunities:Q", title="Listings"),
                tooltip=[alt.Tooltip("Deadline status:N", title="Status"), alt.Tooltip("Opportunities:Q", title="Listings")],
            )
            .properties(height=190)
            .interactive()
        )
        st.altair_chart(deadline_chart, use_container_width=True)
    with detail_cols[1]:
        st.markdown("**Filter pressure**")
        filter_chart = (
            alt.Chart(excluded_rows)
            .mark_bar(cornerRadiusEnd=5, color="#6f8e83")
            .encode(
                y=alt.Y("Filter signal:N", sort="-x", title=None),
                x=alt.X("Listings:Q", title="Listings outside current filter"),
                tooltip=[alt.Tooltip("Filter signal:N", title="Signal"), alt.Tooltip("Listings:Q", title="Listings")],
            )
            .properties(height=190)
            .interactive()
        )
        st.altair_chart(filter_chart, use_container_width=True)
    st.markdown('</section>', unsafe_allow_html=True)


try:
    # This file is small, so read it on each rerun. Caching without a file
    # timestamp can leave the app showing an older directory count after edits.
    opportunities = load_opportunities()
except RuntimeError as error:
    st.error(str(error))
    st.stop()

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand"><div class="brand-mark">J</div><div class="brand-copy"><b>JUMPAD</b><span>Opportunity explorer</span></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<p class="side-eyebrow">Your profile</p><h2 class="side-heading">Make the list yours.</h2>', unsafe_allow_html=True)
    name = st.text_input("Name (optional)", max_chars=60, placeholder="e.g. Alex", key="profile_name")
    grade = st.selectbox("Current grade", list(range(6, 13)), index=3, format_func=lambda value: f"Grade {value}", key="profile_grade")
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="side-eyebrow">Shape your search</p><h2 class="side-heading">What sparks your curiosity?</h2>', unsafe_allow_html=True)
    st.markdown("**Interests**")
    with st.container(key="filter-links"):
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            st.button("Select all", key="select_all", on_click=set_all_subjects, args=(True,), help="Select every interest")
        with link_col2:
            st.button("Clear all", key="clear_all", on_click=set_all_subjects, args=(False,), help="Clear selected interests")
    if "selected_subjects" not in st.session_state:
        st.session_state["selected_subjects"] = ["Computer Science"]
    st.markdown('<div class="interest-picker-cue">Click here <span>↓</span> to choose interests</div>', unsafe_allow_html=True)
    st.multiselect(
        "Choose one or more interests",
        SUBJECTS,
        key="selected_subjects",
        placeholder="Select interests…",
        help="Choose the subjects you want to explore. Select all and Clear all are available above.",
        label_visibility="collapsed",
    )
    preferred_format = st.selectbox("Preferred format", FORMATS, key="preferred_format")
    chosen_type = st.selectbox("Opportunity type", TYPES, key="chosen_type")
    budget = st.slider("Maximum budget", min_value=0, max_value=6000, value=500, step=50, format="$%d", key="budget")
    st.caption("Drag the gold handle, or focus it and use the arrow keys. Steps: $50.")
    st.markdown(
        f'<div class="sidebar-budget"><strong>Up to ${budget:,}</strong><br>$0 <span style="float:right">$6,000</span></div>',
        f'<div class="sidebar-budget"><strong>Current limit: ${budget:,}</strong><br>$0 <span style="float:right">$6,000</span></div>',
        unsafe_allow_html=True,
    )
    st.checkbox("Free only", key="free_only")
    st.caption("Team fees and unconfirmed costs are surfaced for you to check with the organizer.")
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    with st.container(key="reset-button"):
        st.button("Reset all filters", key="reset_all", on_click=reset_filters, help="Restore the default profile and filters")

results, filter_counts = analyze_opportunities(
    opportunities, grade, budget, st.session_state.get("selected_subjects", []), preferred_format, chosen_type, today=TODAY
)
if st.session_state.get("relax_budget", False):
    results, _ = analyze_opportunities(opportunities, grade, 6000, st.session_state.get("selected_subjects", []), preferred_format, chosen_type, today=TODAY)
if st.session_state.get("relax_type", False):
    results, _ = analyze_opportunities(
        opportunities,
        grade,
        6000 if st.session_state.get("relax_budget", False) else budget,
        st.session_state.get("selected_subjects", []),
        preferred_format,
        "Any",
        today=TODAY,
    )
if st.session_state.get("relax_deadline", False):
    results, _ = analyze_opportunities(
        opportunities,
        grade,
        6000 if st.session_state.get("relax_budget", False) else budget,
        st.session_state.get("selected_subjects", []),
        preferred_format,
        "Any" if st.session_state.get("relax_type", False) else chosen_type,
        today=date.min,
    )
if st.session_state.get("free_only", False):
    results = [opp for opp in results if opp.get("cost_known") and opp.get("cost") == 0]

saved_names = set(st.session_state.get("saved_opportunities", []))
count_before_saved_filter = len(results)
user_name = safe(name.strip()) if name.strip() else "your next chapter"

st.markdown(
    f"""
    <section class="hero">
      <div class="hero-copy">
        <div class="hero-kicker">Curated STEM opportunities</div>
        <h1>Find a path<br>toward <em>{user_name}.</em></h1>
        <p>Explore programs, challenges, and experiences shaped around your interests, grade, and goals.</p>
      </div>
      <div class="hero-summary">
        <div class="hero-count"><strong>{count_before_saved_filter}</strong><span>opportunities fit your search right now</span></div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

left_toolbar, middle_toolbar, right_toolbar = st.columns([4.4, 1.4, 1.65])
with left_toolbar:
    st.markdown('<div class="results-toolbar"><div><p class="results-label">Discovery board</p><h2 class="results-title">Your opportunity shortlist</h2></div></div>', unsafe_allow_html=True)
with middle_toolbar:
    with st.container(key="saved-toggle"):
        saved_only = st.checkbox(f"Saved ({len(saved_names)})", key="include_saved_only", help="Show only saved opportunities")
with right_toolbar:
    with st.container(key="sort-wrap"):
        sort_order = st.selectbox("Sort results", ["Best match", "Deadline soonest", "Cost lowest"], key="sort_order")

if saved_only:
    results = [opp for opp in results if opp["name"] in saved_names]

if sort_order == "Deadline soonest":
    results = sorted(results, key=lambda opp: opp["deadline"])
elif sort_order == "Cost lowest":
    results = sorted(
        results,
        key=lambda opp: (not opp["cost_known"], opp["cost"] if opp["cost_known"] else float("inf"), opp["deadline"]),
    )

count = len(results)
st.markdown(
    f'<div class="result-stat"><strong>{count} of {len(opportunities)} opportunities</strong> are currently on your board</div>',
    unsafe_allow_html=True,
)
render_analytics(opportunities, results, filter_counts)

closing = [opp for opp in results if 0 <= (opp["deadline"] - TODAY).days < 14]
if closing:
    closing = sorted(closing, key=lambda opp: opp["deadline"])[:3]
    links = "".join(
        f'<span><a href="{safe(o["link"])}" target="_blank" rel="noopener noreferrer">{safe(o["name"])}</a> · {safe(relative_deadline(o["deadline"])[0])}</span>'
        for o in closing
    )
    st.markdown(
        f'<section class="closing-strip"><div class="closing-title">Closing soon</div><div class="closing-items">{links}</div></section>',
        unsafe_allow_html=True,
    )

if filter_counts["below_grade"]:
    count_word = "listing" if filter_counts["below_grade"] == 1 else "listings"
    st.markdown(
        f'<div class="filter-explainer">{filter_counts["below_grade"]} {count_word} require a higher grade than Grade {grade}. Grade eligibility is informational and can’t be relaxed here.</div>',
        unsafe_allow_html=True,
    )
if filter_counts["deadline_passed"]:
    count_word = "listing" if filter_counts["deadline_passed"] == 1 else "listings"
    st.markdown(
        f'<div class="filter-explainer">{filter_counts["deadline_passed"]} {count_word} have a past deadline.</div>',
        unsafe_allow_html=True,
    )
if filter_counts["budget_unconfirmed"]:
    st.caption(f"{filter_counts['budget_unconfirmed']} currently eligible listing(s) have a team fee or unconfirmed cost.")

relax_options = [
    ("over_budget", f"{filter_counts['over_budget']} over budget", "relax_budget", "Include listings over budget"),
    ("different_type", f"{filter_counts['different_type']} other types", "relax_type", "Include all opportunity types"),
    ("deadline_passed", f"{filter_counts['deadline_passed']} past deadline", "relax_deadline", "Include closed listings"),
]
active_relax = [label for _, label, state_key, _ in relax_options if st.session_state.get(state_key, False)]
with st.container(key="relaxers"):
    if any(filter_counts[key] for key, _, _, _ in relax_options) or active_relax:
        st.markdown('<div class="compact-note"><strong>Keep exploring</strong> · Widen your search without losing your current filters.</div>', unsafe_allow_html=True)
        relax_cols = st.columns(3)
        for col, (count_key, label, state_key, action) in zip(relax_cols, relax_options):
            if filter_counts[count_key] or st.session_state.get(state_key, False):
                text = f"✓ Showing {label}" if st.session_state.get(state_key, False) else f"{label} · show"
                if col.button(text, key=f"toggle_{state_key}", help=action):
                    st.session_state[state_key] = not st.session_state.get(state_key, False)
                    st.rerun()

st.markdown('<h2 class="section-title">Opportunities</h2>', unsafe_allow_html=True)
if results:
    for index, opp in enumerate(results):
        render_card(opp, index, saved_names)
else:
    st.info("No opportunities match these filters yet. Try widening your search or resetting your filters.")
    if st.session_state.get("include_saved_only", False) and not saved_names:
        st.caption("Save an opportunity with the Save button to build your list.")
    st.button("Reset filters", key="empty_reset", on_click=reset_filters)

with st.expander("How matching works"):
    st.write(
        "Grade, budget, deadline, and opportunity type determine eligibility. Your interests and format preference determine ranking; the ranking formula is unchanged. A known individual cost must fit your budget. Team fees and unconfirmed costs remain visible with a reminder to confirm the price. Saved-only and Free-only further narrow the displayed results. Relaxers temporarily include over-budget, other-type, or closed listings, while a higher-grade requirement remains informational."
    )

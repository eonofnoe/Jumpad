import html
import json
from pathlib import Path

import streamlit as st
from matching import MAX_SCORE, match_opportunities, money

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "opportunities.json"
SUBJECTS = ["Computer Science", "Math", "Science", "Engineering", "Physics", "AI"]
TYPES = ["Any", "Competition", "Summer Program", "Internship", "Research", "Scholarship", "Hackathon"]
FORMATS = ["Both", "Online", "Onsite"]

st.set_page_config(page_title="Jumpad | STEM Opportunities", page_icon="🧭", layout="wide")

st.markdown("""
<style>
:root {
  --accent: #0071e3;
  --accent-hover: #0062c4;
  --text: #1d1d1f;
  --secondary: #6e6e73;
  --surface: #ffffff;
  --canvas: #fbfbfd;
  --border: #e5e5e7;
}
.stApp { background: var(--canvas); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Inter", "SF Pro Display", "Segoe UI", sans-serif; }
.block-container { max-width: 1200px; padding: 2.4rem 2rem 4rem; }
[data-testid="stSidebar"] { background: #f7f7f9; border-right: 1px solid var(--border); }
[data-testid="stSidebar"] h3 { color: var(--text); font-size: 1.2rem; letter-spacing: -.02em; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--secondary); line-height: 1.5; }
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background: var(--surface); border: 1px solid #d2d2d7; border-radius: 9px; color: var(--text);
}
[data-testid="stTextInput"] input:focus, [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
  border-color: var(--accent); box-shadow: 0 0 0 3px rgba(0,113,227,.18);
}
[data-testid="stSlider"] [data-testid="stTickBar"] { color: var(--secondary); }
[data-testid="stSlider"] [role="slider"] { background: var(--accent); border-color: var(--accent); }
.slider-limits { display:flex; justify-content:space-between; margin-top:-.65rem; margin-bottom:.85rem; color:var(--secondary); font-size:.74rem; font-variant-numeric:tabular-nums; }
.hero { padding: 1.7rem 0 1.4rem; margin-bottom: 1.15rem; }
.hero-label { color:var(--secondary); font-size:.78rem; font-weight:650; letter-spacing:.02em; margin-bottom:.75rem; }
.hero h1 { color:var(--text); font-size:clamp(2.5rem,5vw,3rem); line-height:1.04; letter-spacing:-.045em; font-weight:700; margin:0 0 .8rem; }
.hero p { color:var(--secondary); max-width:680px; font-size:1.08rem; line-height:1.55; margin:0; }
.intro-row { display:flex; justify-content:space-between; align-items:end; gap:1rem; margin:1.55rem 0 1rem; }
.intro-row h2 { margin:0; color:var(--text); font-size:1.45rem; letter-spacing:-.025em; font-weight:600; }
.intro-row p { color:var(--secondary); margin:.35rem 0 0; font-size:.93rem; }
.stat-strip { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; margin:1.1rem 0 1.8rem; }
.stat { min-height:132px; border:1px solid var(--border); border-radius:14px; background:var(--surface); padding:1.45rem 1.5rem; box-shadow:0 8px 20px rgba(0,0,0,.04); }
.stat-icon { display:flex; align-items:center; justify-content:center; width:34px; height:34px; border-radius:10px; background:#edf5ff; color:var(--accent); font-size:1.05rem; font-weight:700; margin-bottom:.8rem; }
.stat strong { display:block; color:var(--text); font-size:1rem; font-weight:600; margin-bottom:.25rem; }
.stat span { color:var(--secondary); font-size:.82rem; line-height:1.45; }
.section-heading { display:flex; align-items:baseline; gap:.65rem; margin:1.9rem 0 .25rem; }
.section-heading h2 { margin:0; font-size:1.45rem; letter-spacing:-.025em; color:var(--text); font-weight:600; }
.section-heading span { color:var(--secondary); font-size:.86rem; }
.card { background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:1.4rem 1.5rem; margin:.9rem 0 .35rem; box-shadow:0 8px 20px rgba(0,0,0,.04); }
.card-top { display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; }
.card-tags { display:flex; flex-wrap:wrap; gap:.4rem; margin-bottom:.65rem; }
.pill { display:inline-block; border-radius:99px; padding:.28rem .62rem; font-size:.72rem; font-weight:600; background:#f2f2f4; color:#515158; }
.pill.type { background:#f2f2f4; color:#515158; }
.card h3 { margin:0; color:var(--text); font-size:1.22rem; line-height:1.3; letter-spacing:-.02em; font-weight:600; }
.card-desc { margin:.5rem 0 1rem; color:#515158; line-height:1.55; font-size:.93rem; }
.score { flex:0 0 auto; text-align:center; border-radius:11px; padding:.52rem .72rem; background:#f5f5f7; color:#3a3a3c; border:1px solid #e5e5e7; min-width:74px; }
.score strong { display:block; font-size:1rem; line-height:1.2; }
.score span { font-size:.64rem; color:var(--secondary); text-transform:uppercase; letter-spacing:.08em; font-weight:650; }
.metadata { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.6rem; border-top:1px solid #f0f0f2; padding-top:.9rem; }
.meta-item { min-width:0; }
.meta-label { color:var(--secondary); text-transform:uppercase; letter-spacing:.07em; font-weight:600; font-size:.65rem; margin-bottom:.2rem; }
.meta-value { color:#3a3a3c; font-size:.84rem; overflow-wrap:anywhere; }
.reason { margin-top:.9rem; background:#f7f7f9; border-radius:9px; padding:.72rem .85rem; color:#515158; font-size:.82rem; line-height:1.5; }
.stButton>button[kind="primary"] { background:var(--accent); border:1px solid var(--accent); color:white; border-radius:10px; min-height:2.8rem; font-weight:650; transition:background .16s ease, box-shadow .16s ease, transform .16s ease; }
.stButton>button[kind="primary"]:hover { background:var(--accent-hover); border-color:var(--accent-hover); box-shadow:0 4px 12px rgba(0,113,227,.2); transform:translateY(-1px); }
.stButton>button[kind="primary"]:focus-visible, .stLinkButton a:focus-visible { outline:3px solid rgba(0,113,227,.28); outline-offset:2px; }
.stLinkButton a { border-radius:9px; font-weight:600; border-color:var(--border); }
.stLinkButton a:hover { color:var(--accent); border-color:#b7d6f7; }
div[data-testid="stAlert"] { border-radius:12px; }
details { border:1px solid var(--border) !important; border-radius:12px !important; background:var(--surface); }
@media (max-width: 750px) {
  .block-container { padding:1.35rem 1rem 3rem; }
  .hero { padding:1.1rem 0 1rem; }
  .hero h1 { font-size:2.45rem; }
  .stat-strip { grid-template-columns:1fr; gap:.7rem; }
  .stat { min-height:0; padding:1.1rem 1.2rem; }
  .stat-icon { float:left; margin:0 .8rem .4rem 0; }
  .metadata { grid-template-columns:repeat(2,minmax(0,1fr)); row-gap:.85rem; }
  .card { padding:1.1rem; }
  .card-top { gap:.55rem; }
}
@media (max-width: 420px) {
  .score { min-width:61px; padding:.42rem .5rem; }
  .card h3 { font-size:1.08rem; }
}
</style>
""", unsafe_allow_html=True)


def load_opportunities():
    """Load data with a useful error message while keeping parsing out of the UI flow."""
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


@st.cache_data
def cached_opportunities():
    return load_opportunities()


def safe(value):
    return html.escape(str(value), quote=True)


def render_card(opp):
    subjects = ", ".join(opp["subjects"]) or "General"
    reasons = " ".join(opp["reasons"])
    deadline = opp["deadline"].strftime("%b %d, %Y")
    st.markdown(f"""
    <article class="card">
      <div class="card-top">
        <div>
          <div class="card-tags"><span class="pill type">{safe(opp['type'])}</span><span class="pill">{safe(opp['format'])}</span></div>
          <h3>{safe(opp['name'])}</h3>
        </div>
        <div class="score"><strong>{opp['score']}/{MAX_SCORE}</strong><span>match</span></div>
      </div>
      <p class="card-desc">{safe(opp['description'])}</p>
      <div class="metadata">
        <div class="meta-item"><div class="meta-label">Subject</div><div class="meta-value">{safe(subjects)}</div></div>
        <div class="meta-item"><div class="meta-label">Minimum grade</div><div class="meta-value">Grade {opp['grade']}+</div></div>
        <div class="meta-item"><div class="meta-label">Location</div><div class="meta-value">{safe(opp['location'])}</div></div>
        <div class="meta-item"><div class="meta-label">Cost · deadline</div><div class="meta-value">{safe(money(opp['cost']))} · {safe(deadline)}</div></div>
      </div>
      <div class="reason"><strong>Why this appears:</strong> {safe(reasons)}</div>
    </article>
    """, unsafe_allow_html=True)
    st.link_button("View opportunity details ↗", opp["link"])


try:
    opportunities = cached_opportunities()
except RuntimeError as error:
    st.error(str(error))
    st.stop()

st.markdown("""
<section class="hero">
  <div class="hero-label">JUMPAD · YOUR STEM LAUNCHPAD</div>
  <h1>Find your next STEM opportunity.</h1>
  <p>Explore competitions, programs, internships, and research matched to your interests and eligibility.</p>
</section>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Build your profile")
    st.caption("Tell us what you’re looking for. We’ll check eligibility first, then rank the best fits.")
    name = st.text_input("Your name (optional)", max_chars=60, placeholder="e.g. Alex")
    grade = st.selectbox("Current grade", [8, 9, 10, 11, 12], index=1)
    interest = st.selectbox("Main interest", SUBJECTS)
    preferred_format = st.selectbox("Preferred format", FORMATS, help="Choose Both if you have no format preference.")
    chosen_type = st.selectbox("Opportunity type", TYPES)
    budget = st.slider("Maximum budget", min_value=0, max_value=6000, value=500, step=50, format="$%d")
    st.markdown('<div class="slider-limits"><span>$0</span><span>$6,000</span></div>', unsafe_allow_html=True)
    find_button = st.button("Show my matches", type="primary", use_container_width=True)
    st.markdown("---")
    st.caption("Matches are based on the information in each opportunity listing. Confirm current details with the organizer before applying.")

st.markdown('<div class="intro-row"><div><h2>Find the opportunity that fits</h2><p>Use your profile to turn a long list into a clear next step.</p></div></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="stat-strip">
  <div class="stat"><div class="stat-icon">✦</div><strong>{len(opportunities)} opportunities</strong><span>Competitions, programs, research, and internships in one place.</span></div>
  <div class="stat"><div class="stat-icon">✓</div><strong>Eligibility comes first</strong><span>Grade, budget, deadline, and type are checked before ranking.</span></div>
  <div class="stat"><div class="stat-icon">↗</div><strong>Free to explore</strong><span>Paid options within your budget remain in the mix.</span></div>
</div>
""", unsafe_allow_html=True)

if find_button:
    results = match_opportunities(opportunities, grade, budget, interest, preferred_format, chosen_type)
    st.session_state["results"] = results
    st.session_state["search_name"] = name.strip()

if "results" in st.session_state:
    results = st.session_state["results"]
    greeting = f" for {safe(st.session_state['search_name'])}" if st.session_state.get("search_name") else ""
    st.markdown(f'<div class="section-heading"><h2>Your matches{greeting}</h2><span>{len(results)} found</span></div>', unsafe_allow_html=True)
    if results:
        st.caption(f"Ranked by fit · Match score out of {MAX_SCORE}: subject fit (3) and preferred format (2).")
        for opp in results:
            render_card(opp)
    else:
        st.info("No opportunities meet all your selected eligibility filters. Try raising your budget, changing the grade or type, or broadening your preferences.")
else:
    st.markdown('<div class="section-heading"><h2>Ready when you are</h2><span>Set your profile in the sidebar</span></div>', unsafe_allow_html=True)
    st.info("Choose your interests and budget, then select **Show my matches** to see opportunities you’re eligible for.")

with st.expander("How matching works"):
    st.write("We first filter by minimum grade, maximum cost, upcoming deadline, and selected opportunity type. Eligible listings can then earn 3 points for a subject match and up to 2 points for an Online or Onsite format match. Choosing Both means you have no format preference. Cost does not lower a match score.")

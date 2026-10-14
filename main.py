import html
import json
from datetime import date
from pathlib import Path

import streamlit as st
from matching import MAX_SCORE, analyze_opportunities, cost_label

git apply "/Users/noekoumbem/Documents/Codex/2026-10-08/7/jumpad-ui-fixes.patch"
git add main.py .streamlit/config.toml
git commit -m "Polish opportunity card controls and deadline cues"
git push
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "opportunities.json"
SUBJECTS = ["Computer Science", "Math", "Science", "Engineering", "Physics"]
TYPES = ["Any", "Competition", "Summer Program", "Internship", "Research", "Scholarship", "Hackathon"]
FORMATS = ["Both", "Online", "Onsite"]
TODAY = date.today()

st.set_page_config(page_title="Jumpad | STEM Opportunities", page_icon="🧭", layout="wide")

# One cohesive light theme. Streamlit theme colors are also configured in
# .streamlit/config.toml; this block handles app-specific layout and components.
st.markdown("""
<style>
:root {
  --canvas: #fbfbfd;
  --surface: #ffffff;
  --surface-soft: #f4f4f6;
  --border: #d8d8dc;
  --text: #1d1d1f;
  --muted: #59595f;
  --accent: #b84427;
  --accent-soft: #fff0eb;
  --green: #17633c;
  --green-soft: #eaf5ee;
  --radius: 12px;
}
html, body, [class*="st-"], [data-testid="stAppViewContainer"] {
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "SF Pro Display", "Segoe UI", sans-serif;
}
.stApp { background:var(--canvas); color:var(--text); }
.block-container { max-width:1280px; padding:1.15rem 1.6rem 3rem; }
[data-testid="stSidebar"] { background:#f5f5f7; border-right:1px solid var(--border); }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color:var(--text); letter-spacing:-.02em; }
[data-testid="stSidebar"] p, [data-testid="stCaptionContainer"] p { color:var(--muted); font-size:.84rem; line-height:1.45; }
[data-testid="stCaptionContainer"] p { font-size:.84rem !important; }
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label { color:#343439; font-size:.88rem; font-weight:600; }
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background:var(--surface); border:1px solid #c8c8ce; border-radius:var(--radius); color:var(--text); min-height:40px;
}
[data-testid="stTextInput"] input:focus, [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
  border-color:var(--accent); box-shadow:0 0 0 3px rgba(184,68,39,.17);
}
[data-testid="stSlider"] [role="slider"] { background:var(--accent); border-color:var(--accent); }
[data-testid="stSlider"] [data-testid="stTickBar"] { color:var(--muted); }
.app-header { display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; margin:0 0 10px; }
.app-header h1 { margin:0; font-size:1.8rem; line-height:1.15; letter-spacing:-.04em; color:var(--text); }
.app-header p { margin:0; color:var(--muted); font-size:.96rem; }
.result-stat { margin:0 0 14px; color:#39393e; font-size:.94rem; line-height:1.4; }
.result-stat strong { color:var(--text); font-size:1.08rem; }
.eyebrow { color:var(--muted); font-size:.82rem; font-weight:700; letter-spacing:.04em; text-transform:uppercase; }
.chip-row { display:flex; align-items:center; flex-wrap:wrap; gap:8px; margin:8px 0 12px; }
.tag { display:inline-flex; align-items:center; min-height:27px; padding:3px 10px; border-radius:999px; background:#eeeeF1; color:#343439; font-size:.82rem; font-weight:650; }
.tag.type { background:#f2eae7; color:#593124; }
.tag.format { background:#eaf0f6; color:#263d54; }
.tag.free { background:var(--green-soft); color:var(--green); }
.match-badge { display:inline-flex; align-items:center; justify-content:center; min-height:32px; padding:5px 10px; border-radius:999px; background:#f1f1f3; border:1px solid #d8d8dc; color:#303035; font-size:.82rem; font-weight:700; white-space:nowrap; }
.match-badge.strong { background:#eaf5ee; color:#155b38; border-color:#b9d9c5; }
.match-badge.good { background:#fff4e5; color:#704600; border-color:#ead2ad; }
.match-badge.partial { background:#f1f1f3; color:#45454b; }
.desc-clamp { display:-webkit-box; -webkit-box-orient:vertical; -webkit-line-clamp:2; overflow:hidden; margin:4px 0 14px; color:#44444a; font-size:.92rem; line-height:1.48; min-height:2.72em; }
.metadata { display:grid; grid-template-columns:1fr 1fr 1.25fr 1fr 1.5fr; gap:12px; padding:12px 0; border-top:1px solid #e7e7e9; border-bottom:1px solid #e7e7e9; }
.meta-item { min-width:0; }
.meta-label { margin-bottom:4px; color:var(--muted); font-size:.82rem; font-weight:700; letter-spacing:.01em; }
.meta-value { color:#303035; font-size:.88rem; line-height:1.4; overflow-wrap:anywhere; }
.deadline .meta-value { font-weight:750; }
.deadline.soon .meta-value, .deadline.closed .meta-value { color:var(--accent); }
.why-line { margin:10px 0 4px; color:#36363b; font-size:.89rem; line-height:1.4; }
.closing-strip { padding:10px 12px; margin:0 0 12px; border:1px solid #e2c2b8; border-radius:var(--radius); background:#fff7f4; }
.closing-title { margin:0 0 6px; color:#74321f; font-size:.86rem; font-weight:750; }
.closing-items { display:flex; flex-wrap:wrap; gap:8px 16px; color:#503b35; font-size:.85rem; }
.closing-items a { color:#76351f; font-weight:700; text-decoration:underline; text-underline-offset:2px; }
.compact-note { color:var(--muted); font-size:.84rem; line-height:1.4; }
.section-title { margin:10px 0 4px; color:var(--text); font-size:1.25rem; letter-spacing:-.02em; }
.opportunity-title { color:var(--text); font-size:1.16rem; line-height:1.3; font-weight:750; letter-spacing:-.02em; text-decoration:none; }
.opportunity-title:hover { color:#78321e; text-decoration:underline; text-underline-offset:3px; }
.st-key-filter-links button, .st-key-relaxers button, .st-key-reset-button button {
  min-height:36px; padding:4px 7px; border:0; background:transparent; color:#6f2c1b; text-decoration:underline; text-underline-offset:3px; font-size:.86rem; box-shadow:none;
}
.st-key-filter-links button, .st-key-relaxers button, .st-key-reset-button button { border-radius:var(--radius) !important; }
.st-key-filter-links button:hover, .st-key-relaxers button:hover, .st-key-reset-button button:hover { color:#822f17; background:#f6e9e4; }
.st-key-opportunity-list [data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--border); border-radius:var(--radius); background:var(--surface); box-shadow:0 5px 16px rgba(0,0,0,.035); transition:border-color .16s ease, box-shadow .16s ease; }
.st-key-opportunity-list [data-testid="stVerticalBlockBorderWrapper"]:hover { border-color:#b9a49d; box-shadow:0 8px 20px rgba(0,0,0,.07); }
[data-testid="stExpander"] { border-color:var(--border); border-radius:var(--radius); background:var(--surface); }
[data-testid="stLinkButton"] a { min-height:40px; border-radius:var(--radius); border-color:var(--border); color:#343439; font-weight:650; }
[data-testid="stLinkButton"] a:hover { border-color:#a69d99; color:#712e1c; }
[data-testid="stButton"] button, [data-testid="stCheckbox"] label { min-height:40px; }
@media (max-width: 800px) {
  .block-container { padding:1rem 1rem 2.5rem; }
  .metadata { grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px 12px; }
}
@media (max-width: 640px) {
  .app-header { gap:5px; align-items:flex-start; flex-direction:column; }
  .app-header h1 { font-size:1.65rem; }
  .metadata { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .st-key-opportunity-list [data-testid="stHorizontalBlock"] { gap:.5rem; }
  .st-key-opportunity-list [data-testid="stButton"] button { min-height:44px; }
}
</style>
""", unsafe_allow_html=True)


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
            st.markdown(f'<a class="opportunity-title" href="{safe(opp["link"])}" target="_blank" rel="noopener noreferrer">{safe(name)} ↗</a>', unsafe_allow_html=True)
        with badge_col:
            st.markdown(f'<span class="match-badge {badge_class}" title="{safe(badge_detail)}">{badge}</span>', unsafe_allow_html=True)
        with save_col:
            if st.button("Saved ✓" if is_saved else "Save", key=key, help="Save this opportunity" if not is_saved else "Remove from saved opportunities"):
                updated = set(st.session_state.get("saved_opportunities", []))
                if name in updated:
                    updated.remove(name)
                else:
                    updated.add(name)
                st.session_state["saved_opportunities"] = sorted(updated)
                st.rerun()

        type_tag, format_tag = st.columns([1, 5])
        with type_tag:
            st.markdown(f'<span class="tag type">{safe(opp["type"])}</span>', unsafe_allow_html=True)
        with format_tag:
            st.markdown(f'<span class="tag format">{safe(opp["format"])}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="desc-clamp">{safe(opp["description"])}</div>', unsafe_allow_html=True)
        subjects = ", ".join(opp["subjects"]) or "General"
        grade_class = "meta-item"
        cost_display = f'<span class="tag free">Free</span>' if free else safe(price)
        deadline_markup = f'<div class="meta-item deadline {deadline_class}"><div class="meta-label">Deadline</div><div class="meta-value">{safe(deadline_date)}<br>{safe(relative)}</div></div>'
        st.markdown(f"""
        <div class="metadata">
          <div class="meta-item"><div class="meta-label">Subject</div><div class="meta-value">{safe(subjects)}</div></div>
          <div class="{grade_class}"><div class="meta-label">Minimum grade</div><div class="meta-value">{safe(opp['grade_label'])}</div></div>
          <div class="meta-item"><div class="meta-label">Location</div><div class="meta-value">{safe(opp['location'])}</div></div>
          <div class="meta-item"><div class="meta-label">Cost</div><div class="meta-value">{cost_display}</div></div>
          {deadline_markup}
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="why-line"><strong>Why it matches:</strong> {safe(" ".join(opp["reasons"]))}</div>', unsafe_allow_html=True)
        with st.expander("See eligibility details", expanded=False):
            for check in opp["eligibility_checks"]:
                if opp["deadline"] < TODAY and check.startswith("Deadline ("):
                    check = f"Deadline ({opp['deadline'].isoformat()}) has passed; this listing is shown because closed listings are included. Check the organizer for a new cycle."
                st.markdown(f"- {safe(check)}")
        st.link_button("View details ↗", opp["link"])
        st.caption(badge_detail)


try:
    # This file is small, so read it on each rerun. Caching without a file
    # timestamp can leave the app showing an older directory count after edits.
    opportunities = load_opportunities()
except RuntimeError as error:
    st.error(str(error))
    st.stop()

with st.sidebar:
    st.markdown("### About you")
    name = st.text_input("Name (optional)", max_chars=60, placeholder="e.g. Alex", key="profile_name")
    grade = st.selectbox("Current grade", list(range(6, 13)), index=3, format_func=lambda value: f"Grade {value}", key="profile_grade")
    st.markdown("### What you want")
    st.markdown("**Interests**")
    with st.container(key="filter-links"):
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            st.button("Select all", key="select_all", on_click=set_all_subjects, args=(True,), help="Select every interest")
        with link_col2:
            st.button("Clear all", key="clear_all", on_click=set_all_subjects, args=(False,), help="Clear selected interests")
    # Checkboxes provide compact multi-select and avoid the empty "No results"
    # dropdown that can remain open after selecting every option.
    if "selected_subjects" not in st.session_state:
        st.session_state["selected_subjects"] = ["Computer Science"]
    selected_before_run = set(st.session_state.get("selected_subjects", []))
    for subject in SUBJECTS:
        key = subject_key(subject)
        if key not in st.session_state:
            st.session_state[key] = subject in selected_before_run
    interest_cols = st.columns(2)
    for index, subject in enumerate(SUBJECTS):
        with interest_cols[index % 2]:
            st.checkbox(subject, key=subject_key(subject))
    st.session_state["selected_subjects"] = [subject for subject in SUBJECTS if st.session_state.get(subject_key(subject), False)]
    preferred_format = st.selectbox("Preferred format", FORMATS, key="preferred_format")
    chosen_type = st.selectbox("Opportunity type", TYPES, key="chosen_type")
    budget = st.slider("Maximum budget", min_value=0, max_value=6000, value=500, step=50, format="$%d", key="budget")
    st.markdown(f'<div class="compact-note"><strong>Up to ${budget:,}</strong><br>$0 <span style="float:right">$6,000</span></div>', unsafe_allow_html=True)
    st.checkbox("Free only", key="free_only")
    st.caption("Team fees and unconfirmed costs are surfaced for you to check with the organizer.")
    st.divider()
    with st.container(key="reset-button"):
        st.button("Reset all filters", key="reset_all", on_click=reset_filters, help="Restore the default profile and filters")

st.markdown('<header class="app-header"><h1>Jumpad</h1><p>Find your next STEM opportunity.</p></header>', unsafe_allow_html=True)

results, filter_counts = analyze_opportunities(
    opportunities, grade, budget, st.session_state.get("selected_subjects", []), preferred_format, chosen_type
)
if st.session_state.get("relax_budget", False):
    results, _ = analyze_opportunities(opportunities, grade, 6000, st.session_state.get("selected_subjects", []), preferred_format, chosen_type)
if st.session_state.get("relax_type", False):
    results, _ = analyze_opportunities(opportunities, grade, 6000 if st.session_state.get("relax_budget", False) else budget, st.session_state.get("selected_subjects", []), preferred_format, "Any")
if st.session_state.get("relax_deadline", False):
    results, _ = analyze_opportunities(opportunities, grade, 6000 if st.session_state.get("relax_budget", False) else budget, st.session_state.get("selected_subjects", []), preferred_format, "Any" if st.session_state.get("relax_type", False) else chosen_type, today=date.min)
if st.session_state.get("free_only", False):
    results = [opp for opp in results if opp.get("cost_known") and opp.get("cost") == 0]

saved_names = set(st.session_state.get("saved_opportunities", []))
if st.checkbox(f"Saved ({len(saved_names)})", key="include_saved_only", help="Show only saved opportunities"):
    results = [opp for opp in results if opp["name"] in saved_names]

sort_col, _ = st.columns([1.4, 5])
with sort_col:
    sort_order = st.selectbox("Sort results", ["Best match", "Deadline soonest", "Cost lowest"], label_visibility="collapsed", key="sort_order")
if sort_order == "Deadline soonest":
    results = sorted(results, key=lambda opp: opp["deadline"])
elif sort_order == "Cost lowest":
    results = sorted(results, key=lambda opp: (not opp["cost_known"], opp["cost"] if opp["cost_known"] else float("inf"), opp["deadline"]))

count = len(results)
st.markdown(f'<div class="result-stat"><strong>{len(opportunities)} opportunities listed</strong> · {count} currently fit your filters</div>', unsafe_allow_html=True)

closing = [opp for opp in results if 0 <= (opp["deadline"] - TODAY).days < 14]
if closing:
    closing = sorted(closing, key=lambda opp: opp["deadline"])[:3]
    links = "".join(f'<span><a href="{safe(o["link"])}" target="_blank" rel="noopener noreferrer">{safe(o["name"])}</a> · Closes in {(o["deadline"] - TODAY).days} days</span>' for o in closing)
    st.markdown(f'<section class="closing-strip"><div class="closing-title">Closing soon</div><div class="closing-items">{links}</div></section>', unsafe_allow_html=True)

if filter_counts["below_grade"]:
    st.caption(f"{filter_counts['below_grade']} listing(s) require a higher grade than Grade {grade}; grade eligibility is informational and can’t be relaxed here.")
if filter_counts["deadline_passed"]:
    st.caption(f"{filter_counts['deadline_passed']} listing(s) have a past deadline.")
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
        st.markdown('<div class="compact-note"><strong>Try widening your search</strong></div>', unsafe_allow_html=True)
        st.caption("Counts are independent and may overlap when a listing misses more than one filter.")
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
    st.write("Grade, budget, deadline, and opportunity type determine eligibility. Your interests and format preference determine ranking; the ranking formula is unchanged. A known individual cost must fit your budget. Team fees and unconfirmed costs remain visible with a reminder to confirm the price. Saved-only and Free-only further narrow the displayed results. Relaxers temporarily include over-budget, other-type, or closed listings, while a higher-grade requirement remains informational.")

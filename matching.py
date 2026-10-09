"""Pure opportunity validation and matching helpers."""
from datetime import date
import math
from urllib.parse import urlparse

MAX_SCORE = 5


def normalize_subjects(opp):
    subjects = opp.get("Subjects", [])
    if isinstance(subjects, str):
        subjects = [subjects]
    elif not isinstance(subjects, list):
        subjects = []
    legacy = opp.get("Subject")
    values = [*subjects, *([legacy] if isinstance(legacy, str) else [])]
    return list(dict.fromkeys(s.strip() for s in values if isinstance(s, str) and s.strip()))


def parse_opportunity(opp):
    if not isinstance(opp, dict):
        return None
    name, grade, cost = opp.get("Name"), opp.get("Grade"), opp.get("Cost")
    deadline_raw, url, fmt = opp.get("Deadline"), opp.get("Link"), opp.get("Format")
    if not isinstance(name, str) or not name.strip():
        return None
    if isinstance(grade, bool) or not isinstance(grade, int) or not 0 <= grade <= 12:
        return None
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0:
        return None
    try:
        deadline = date.fromisoformat(deadline_raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(fmt, str) or not isinstance(url, str):
        return None
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return None
    return {"name":name.strip(), "grade":grade, "cost":cost, "deadline":deadline,
            "format":fmt, "type":opp.get("Type", ""), "subjects":normalize_subjects(opp),
            "location":opp.get("Location", "Not specified"),
            "description":opp.get("Description", "Description not provided"), "link":url,
            "source":opp}


def match_opportunities(records, grade, budget, subject, preferred_format, chosen_type, today=None):
    today = today or date.today()
    matches = []
    for raw in records:
        opp = parse_opportunity(raw)
        if not opp:
            continue
        if grade < opp["grade"] or budget < opp["cost"] or opp["deadline"] < today:
            continue
        if chosen_type != "Any" and opp["type"] != chosen_type:
            continue
        score, reasons = 0, ["Meets the minimum grade, budget, and upcoming-deadline requirements."]
        if subject in opp["subjects"]:
            score += 3
            reasons.append(f"Matches your subject interest: {subject}.")
        if preferred_format != "Both" and (opp["format"].lower() == "both" or preferred_format.lower() == opp["format"].lower()):
            score += 2
            reasons.append(f"Supports your format preference ({preferred_format}).")
        matches.append({**opp, "score":score, "reasons":reasons})
    return sorted(matches, key=lambda item:item["score"], reverse=True)


def money(value):
    return "Free" if value == 0 else f"${value:,.0f}" if float(value).is_integer() else f"${value:,.2f}"

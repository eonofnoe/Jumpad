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
    cost_known = cost is not None
    if cost_known and (isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0):
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
    cost_basis = str(opp.get("CostBasis", "individual" if cost_known else "unknown")).strip().lower()
    grade_label = opp.get("GradeLabel") or f"Grade {grade}+"
    return {"name":name.strip(), "grade":grade, "grade_label":grade_label,
            "cost":cost, "cost_basis":cost_basis, "cost_known":cost_known, "deadline":deadline,
            "format":fmt, "type":opp.get("Type", ""), "subjects":normalize_subjects(opp),
            "location":opp.get("Location", "Not specified"),
            "description":opp.get("Description", "Description not provided"), "link":url,
            "source":opp}


def analyze_opportunities(records, grade, budget, subjects, preferred_format, chosen_type, today=None):
    """Return ranked eligible results and independent counts for each eligibility filter."""
    today = today or date.today()
    selected_subjects = [subjects] if isinstance(subjects, str) else list(subjects or [])
    matches = []
    counts = {
        "valid": 0,
        "below_grade": 0,
        "over_budget": 0,
        "budget_unconfirmed": 0,
        "deadline_passed": 0,
        "different_type": 0,
        "invalid": 0,
    }

    for raw in records:
        opp = parse_opportunity(raw)
        if not opp:
            counts["invalid"] += 1
            continue
        counts["valid"] += 1

        grade_ok = grade >= opp["grade"]
        budget_confirm = opp["cost_basis"] in ("per team", "unknown") or not opp["cost_known"]
        budget_ok = budget_confirm or budget >= opp["cost"]
        deadline_ok = opp["deadline"] >= today
        type_ok = chosen_type == "Any" or chosen_type == opp["type"]

        counts["below_grade"] += not grade_ok
        counts["over_budget"] += not budget_confirm and not budget_ok
        counts["budget_unconfirmed"] += budget_confirm and grade_ok and deadline_ok and type_ok
        counts["deadline_passed"] += not deadline_ok
        counts["different_type"] += not type_ok
        if not (grade_ok and budget_ok and deadline_ok and type_ok):
            continue

        matching_subjects = [subject for subject in selected_subjects if subject in opp["subjects"]]
        score, reasons = 0, []
        if opp["grade"] == 0:
            grade_check = f"The listing states {opp['grade_label']}; confirm any age or school-status rules with the organizer."
        else:
            grade_check = f"Your grade ({grade}) meets {opp['grade_label']}."
        if opp["cost_basis"] == "per team":
            budget_check = f"Team fee is {money(opp['cost'])}; your personal share is unknown, so confirm it with an advisor (your budget is {money(budget)})."
        elif not opp["cost_known"] or opp["cost_basis"] == "unknown":
            budget_check = "The organizer page does not clearly state the entry cost; confirm the fee before applying."
        else:
            budget_check = f"Cost ({money(opp['cost'])}) is within your budget ({money(budget)})."
        eligibility_checks = [
            grade_check,
            budget_check,
            f"Deadline ({opp['deadline'].isoformat()}) has not passed.",
        ]
        if chosen_type != "Any":
            eligibility_checks.append(f"Type matches your selection: {chosen_type}.")
        else:
            eligibility_checks.append("Included across opportunity types (Any selected).")

        if matching_subjects:
            score += 3
            reasons.append("Matches your interests: " + ", ".join(matching_subjects) + ".")
        if preferred_format != "Both" and (
            opp["format"].lower() == "both" or preferred_format.lower() == opp["format"].lower()
        ):
            score += 2
            reasons.append(f"Supports your format preference ({preferred_format}).")
        if not reasons:
            reasons.append("Meets your eligibility filters; it may still be worth exploring.")
        matches.append({**opp, "score":score, "reasons":reasons, "eligibility_checks":eligibility_checks})

    return sorted(matches, key=lambda item:item["score"], reverse=True), counts


def match_opportunities(records, grade, budget, subject, preferred_format, chosen_type, today=None):
    """Return ranked results; accepts a subject string or a collection of subjects."""
    matches, _ = analyze_opportunities(records, grade, budget, subject, preferred_format, chosen_type, today)
    return matches


def money(value):
    return "Free" if value == 0 else f"${value:,.0f}" if float(value).is_integer() else f"${value:,.2f}"


def cost_label(opportunity):
    if not opportunity.get("cost_known", True) or opportunity.get("cost_basis") == "unknown":
        return "Cost not confirmed"
    amount = money(opportunity["cost"])
    if opportunity.get("cost_basis") == "per team":
        return f"{amount} per team"
    if opportunity.get("cost_basis") == "per student":
        return f"{amount} per student"
    return amount

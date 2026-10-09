# Jumpad

A Streamlit app that filters STEM opportunities by grade, budget, deadline, and type, then ranks eligible results by subject and (when selected) Online/Onsite format fit.

## Run locally

1. Use Python 3.10 or newer.
2. From this folder, install the dependency: `python -m pip install -r requirements.txt`.
3. Start the app: `streamlit run main.py`.

The opportunity data lives in `opportunities.json`. If you edit it while the app is open, use Streamlit's **Clear cache** command and rerun the app.

## Data notes

The supplied 32 records are preserved. The file parses as valid JSON, the records have unique names, and required matching fields use expected types. One record, CyberPatriot National Youth Cyber Defense Competition, has a deadline of 2026-10-01, which is already past as of 2026-10-08; it remains in the data and is filtered out automatically. Deadlines and program details can vary by cycle, so confirm dates, eligibility, costs, formats, and links on the linked official pages before applying. The dataset has not been independently verified against every linked organization.

## Manual check

- Search with grade 9, budget $0, and a CS interest; confirm free eligible opportunities appear.
- Set the budget to $0 and choose a paid record's maximum grade/type; confirm it is excluded.
- Check the grade boundary (a grade equal to the minimum is eligible).
- Use a past deadline and confirm it is excluded; check an upcoming deadline remains eligible.
- Switch the type from Any to a specific type and confirm the results narrow.
- Compare Online, Onsite, and Both format choices; Both does not add format points.
- Confirm scores are out of 5, sorted high to low, and explain only supported subject/format matches.
- Try filters with no eligible records and confirm the empty-state guidance appears.
- Open a result link and test the layout at a narrow/mobile window width.

## Demo video outline (1–3 minutes)

1. Introduce the student problem and explain that the app narrows opportunities using a profile.
2. Enter an example grade, subject, format, budget, and type; briefly narrate the eligibility filters.
3. Show the ranked cards, match score, reasons, deadline, cost, and official link.
4. Change one filter (for example budget or format) to demonstrate how the list changes.
5. Close by noting that users should confirm current cycle details on the official opportunity pages.

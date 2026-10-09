# Jumpad

**Jumpad** helps high school students find STEM competitions, summer programs, internships, research programs, and other learning opportunities that fit their profile.

Students choose a grade, subject interest, preferred format, opportunity type, and budget. Jumpad filters out listings that do not meet the selected eligibility requirements, then ranks the remaining opportunities and explains each match.

## Features

- Filter by minimum grade, maximum cost, upcoming deadline, and opportunity type.
- Rank eligible results by subject match and preferred Online or Onsite format.
- Show a clear match score out of 5, with reasons for the score.
- Display subjects, grade, format, location, cost, deadline, and a link to each opportunity.
- Handle both the newer `Subjects` list and legacy `Subject` string fields in the data.
- Adapt the layout for desktop and mobile-sized screens.

A user's budget is an eligibility filter, not a ranking penalty. Choosing **Both** for format means there is no format preference, so it adds no format points.

## Run locally

You need Python 3.10 or newer.

1. Open a terminal in the Jumpad project folder.
2. Install the app dependency:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Start Jumpad:

   ```bash
   streamlit run main.py
   ```

4. Open the local address printed in the terminal, usually `http://localhost:8501`.

To stop the local app, press **Control-C** in the terminal.

## Deploy as a website

Jumpad can be hosted with [Streamlit Community Cloud](https://share.streamlit.io/):

1. Upload `main.py`, `matching.py`, `opportunities.json`, and `requirements.txt` to the root of a GitHub repository.
2. Sign in to Streamlit Community Cloud with GitHub and choose **Create app**.
3. Select the repository, branch, and `main.py` as the app file, then deploy.
4. Share the resulting `*.streamlit.app` URL.

A public repository makes the source code public. Do not add private data, passwords, or API keys to the repository. Streamlit Cloud redeploys the app when changes are pushed to the selected branch.

## Project files

```text
main.py             Streamlit interface and data loading
matching.py         Opportunity validation, eligibility, and ranking logic
opportunities.json  Opportunity listings
requirements.txt    Python package requirements
test_matching.py    Focused tests for matching behavior
README.md           Project guide
```

## How matching works

Jumpad first checks eligibility:

1. The selected grade meets or exceeds the listing's minimum grade.
2. The listing cost is within the selected budget.
3. The deadline is today or in the future.
4. If a specific opportunity type is selected, the listing has that type.

Eligible listings can earn up to **3 points** for matching the selected subject and **2 points** for matching an Online or Onsite format preference. Results are sorted from highest to lowest score. Cost does not reduce the score.

Malformed records that cannot be safely evaluated are skipped instead of stopping the app. Subject fields are read without modifying the source dataset.

## Opportunity data

The supplied dataset contains 32 listings. It is valid JSON and contains no duplicate names. As of October 8, 2026, the CyberPatriot listing has a past deadline; it is retained in the file and excluded from results automatically.

Program dates, fees, formats, eligibility, and links can change. The dataset has not been independently verified against every organizer. Students should confirm current-cycle details on the linked official pages before applying. To update listings, edit `opportunities.json`; if the app is already running, clear Streamlit's cache and rerun it.

## Run the tests

From the project folder:

```bash
python3 -m unittest -v test_matching.py
```

The tests cover grade and budget boundaries, expired deadlines, type filters, result sorting, subject-field compatibility, malformed records, and the meaning of the **Both** format choice.

## Manual review checklist

- Try a zero-dollar budget and confirm paid opportunities are excluded.
- Set the budget exactly to an opportunity's cost and confirm it remains eligible.
- Try a grade equal to the minimum grade and confirm it qualifies.
- Confirm past-deadline listings are excluded and upcoming ones can appear.
- Select a specific type and confirm results narrow to that type.
- Compare Online, Onsite, and Both format preferences.
- Confirm results are sorted by score and each explanation reflects the listing data.
- Try a profile with no eligible results and check the empty-state guidance.
- Open an opportunity link and check the layout at a narrow/mobile width.

## 1–3 minute demo video outline

1. Introduce the challenge of finding STEM opportunities that fit a student's profile.
2. Enter a sample grade, subject, format, type, and budget.
3. Show the ranked cards, scores, match explanations, deadlines, costs, and organizer links.
4. Change one filter and show how eligibility or ranking changes.
5. End by reminding viewers to verify current details with the opportunity organizer.

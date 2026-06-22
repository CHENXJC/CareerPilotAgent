# CareerPilotAgent Manual QA Checklist

Use this checklist after installing requirements and starting the app with:

```powershell
Set-Location F:\AIProjects\CareerPilotAgent
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Run Check

- [ ] `streamlit run app.py` opens successfully
- [ ] No import errors
- [ ] No missing file errors

## Profile Check

- [ ] Demo Profile displays safely and is read-only
- [ ] Local Private Profile mode appears
- [ ] A missing private profile shows the creation button
- [ ] Create Local Private Profile from Demo works
- [ ] Save Local Profile works
- [ ] Reload Local Profile works
- [ ] Reset from Demo Profile works
- [ ] `data/private/user_profile.json` is created locally
- [ ] `data/private/` is ignored by Git
- [ ] Active profile affects scoring, resume suggestions, cover letter, and report
- [ ] No private profile data appears in README or public documentation

## JD Analysis Check

- [ ] Sample Marketing JD loads
- [ ] Sample Business Analyst JD loads
- [ ] Custom pasted JD works
- [ ] Category and seniority are detected

## Fit Score Check

- [ ] Total score appears
- [ ] Dimension scores appear
- [ ] Priority label appears
- [ ] Matched and missing skills appear
- [ ] Risk flags appear

## Resume Suggestion Check

- [ ] Keywords appear
- [ ] Bullet suggestions are realistic
- [ ] Portfolio project suggestions appear
- [ ] No fake work-experience claims

## Cover Letter Check

- [ ] Draft appears
- [ ] Placeholders remain editable
- [ ] TXT download works

## Tracker Check

- [ ] Form validates company and role
- [ ] Application can be saved
- [ ] Tracker table displays saved rows
- [ ] CSV download works

## Export Check

- [ ] Markdown preview appears
- [ ] Markdown download works

## Safety Check

- [ ] No API keys
- [ ] No real resume data
- [ ] No private contact details
- [ ] No auto-apply
- [ ] No scraping
- [ ] No email sending

## Public Showcase Check

- [ ] README accurately describes the implemented project
- [ ] Screenshot section does not reference missing files
- [ ] `PUBLIC_SHOWCASE_MANIFEST.md` exists
- [ ] `tools/public_safety_check.py` runs successfully
- [ ] `data/private/` is ignored
- [ ] Demo Profile is selected for every public screenshot
- [ ] No private profile data appears in documentation or showcase notes
- [ ] No external API, scraping, auto-apply, or email-sending logic exists
- [ ] Git status contains no virtual environment, cache, log, private, or generated-output files

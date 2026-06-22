# Public Showcase Manifest

## Project

CareerPilotAgent

## Current Checkpoint

CAREER-005-GITHUB-PUBLIC-SHOWCASE

## Published Repository

- URL: `https://github.com/CHENXJC/CareerPilotAgent`
- Initial showcase commit: `cdba5dbe827ae56613fae26efb50f79135d5d13e`
- Visibility: Public

## Public Files Expected

- `app.py`
- `README.md`
- `requirements.txt`
- `.gitignore`
- `PROJECT_STATUS.md`
- `PUBLIC_SHOWCASE_MANIFEST.md`
- `career_pilot/`
- `data/sample_jobs.csv`
- `data/sample_profile.json`
- `data/application_tracker.csv`
- `docs/`
- `tests/`
- `tools/`
- `portfolio/showcase_screenshots/01_home_hero.png`
- `portfolio/showcase_screenshots/02_demo_profile.png`
- `portfolio/showcase_screenshots/03_jd_analyzer.png`
- `portfolio/showcase_screenshots/04_fit_score.png`
- `portfolio/showcase_screenshots/05_resume_suggestions.png`
- `portfolio/showcase_screenshots/06_cover_letter_draft.png`
- `portfolio/showcase_screenshots/07_application_tracker.png`
- `portfolio/showcase_screenshots/08_export_report.png`
- `portfolio/showcase_notes/`

Generated cache folders are not public showcase content.

## Must Not Be Published

- `data/private/`
- `data/private/user_profile.json`
- `.env` and `.env.*`
- `.venv/` and `venv/`
- `__pycache__/` and `.pytest_cache/`
- `outputs/*`
- Real resumes or application records
- Private contact details or identity numbers
- API keys, passwords, or tokens
- Browser cookies or session storage
- Job-board login data

## Safety Boundary

The public project performs local rule-based analysis only. It does not scrape job boards, auto-apply, send email, call an external API, or commit a private resume. Demo Profile is the only profile intended for public screenshots.

## Pre-Push Checks

- [ ] Run `python -m pytest`
- [ ] Run `python tools/public_safety_check.py`
- [ ] Inspect `git status` and `git diff`
- [ ] Verify `data/private/` is ignored and untracked
- [ ] Review every README screenshot reference
- [ ] Confirm no private data appears in documentation or tracker rows
- [ ] Confirm caches, virtual environments, logs, and generated outputs are excluded

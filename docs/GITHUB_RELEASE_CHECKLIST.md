# GitHub Release Checklist

## CAREER-005 Verification Record

- Screenshot set: 8 reviewed Demo Profile images
- Automated tests: `14 passed`
- Public safety check: `PASS` with documentation/context review warnings only
- Target repository: `https://github.com/CHENXJC/CareerPilotAgent`
- Private profile and virtual environment: must remain ignored and untracked
- Initial public showcase commit: `cdba5dbe827ae56613fae26efb50f79135d5d13e`
- Push status: successful on `main`
- Remote review: README and 8 screenshots present; private profile absent

## Before Commit

- [ ] Run the complete test suite
- [ ] Run the public safety check
- [ ] Inspect `git status`
- [ ] Confirm `data/private/` is not tracked
- [ ] Confirm `.env`, `.venv`, caches, logs, and outputs are not staged
- [ ] Confirm no private contact details or real application records exist
- [ ] Confirm README statements match the implemented features
- [ ] Confirm screenshots are safe if any are included

## Before Push

- [ ] Review `git diff`
- [ ] Review `.gitignore`
- [ ] Run `python tools/public_safety_check.py`
- [ ] Run `python -m pytest`
- [ ] Confirm no accidental local files are staged
- [ ] Confirm every README image path points to an existing reviewed file

## After Push

- [ ] Open the GitHub repository and confirm README rendering
- [ ] Confirm screenshot links work, if screenshots were added
- [ ] Confirm the About description is accurate
- [ ] Add relevant GitHub topics
- [ ] Pin the repository only after the final public review

## Suggested GitHub About

Local-first AI job matching and application assistant for JD analysis, fit scoring, resume suggestions, cover letters, and application tracking.

## Suggested Topics

`python` · `streamlit` · `career` · `job-search` · `resume` · `ai-agent` · `automation` · `portfolio-project` · `local-first` · `privacy-first`

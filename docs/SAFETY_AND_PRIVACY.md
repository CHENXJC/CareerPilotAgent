# Safety and Privacy

CareerPilotAgent ships with synthetic demo data only. The sample profile does not represent a real person and contains no email address, phone number, street address, account credentials, or private resume.

## Safe use

- Keep real resumes and private notes outside a public repository.
- Never commit `.env` files, API keys, passwords, or job-board credentials.
- Review every generated statement. Do not present coursework or portfolio projects as paid employment.
- Apply manually; the project contains no auto-apply or email-sending logic.
- Treat tracker notes as private if you replace the demo CSV with personal data.

## Public Showcase vs Private Personal Data

The code, synthetic job descriptions, and demo profile are suitable for a public showcase. A user's real resume, contact details, application history, interview notes, visa details, and employer correspondence are private personal data and should remain in ignored local storage such as `data/private/`.

## Local Private Profile

`data/private/user_profile.json` is an optional local-only profile used by the editor. The entire `data/private/` directory is ignored by Git.

Recommended fields are general background, skills, tools, portfolio projects, target roles, preferred locations, strengths, and general availability such as part-time or internship.

Do not store highly sensitive information, including:

- Phone numbers or private email addresses
- Passport, visa, or student ID numbers
- Exact home addresses
- Account passwords or recovery information
- API keys or access tokens

Git ignore rules reduce accidental commits; they do not turn the file into a secure vault. Keep entries minimal and appropriate for local career planning.

## Public Showcase Mode

Use **Demo Profile** for screenshots, demonstrations, and GitHub. Do not commit, publish, or screenshot the Local Private Profile. Before preparing showcase assets, confirm that `data/private/` is ignored and that the app is switched back to Demo Profile.

## CAREER-004 Public Release Review

Before any public commit or push:

1. Run `python -m pytest`.
2. Run `python tools/public_safety_check.py`.
3. Review `PUBLIC_SHOWCASE_MANIFEST.md` and `docs/GITHUB_RELEASE_CHECKLIST.md`.
4. Inspect the complete Git staging area and diff.
5. Confirm screenshots use Demo Profile and contain no local notifications or private tracker data.

The safety checker deliberately skips `data/private/`, virtual environments, caches, and generated outputs because none of those paths belongs in the public tree. Their exclusion must also be confirmed through Git status before release.

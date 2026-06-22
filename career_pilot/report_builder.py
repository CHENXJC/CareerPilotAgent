"""Markdown export builder."""

from __future__ import annotations


def _bullets(items: list[str], empty: str = "None detected") -> str:
    return "\n".join(f"- {item}" for item in items) if items else f"- {empty}"


def build_markdown_report(job_data: dict, fit_result: dict, resume_suggestions: dict, cover_letter: str) -> str:
    dimensions = [f"{name}: {score}" for name, score in fit_result.get("dimension_scores", {}).items()]
    projects = [
        item.get("name", str(item)) if isinstance(item, dict) else str(item)
        for item in resume_suggestions.get("projects_to_highlight", fit_result.get("recommended_projects", []))
    ]
    return f"""# CareerPilotAgent Analysis Report

## 1. Job Summary

- Role: {job_data.get('role_title', '[Role Title]')}
- Company: {job_data.get('company_name', '[Company Name]')}
- Category: {job_data.get('job_category', 'General Business')}
- Seniority: {job_data.get('seniority_level', 'Unknown')}
- Active profile: {fit_result.get('profile_name', 'Selected Profile')}

## 2. Fit Score Summary

**{fit_result.get('total_score', 0)}/100 — {fit_result.get('priority_label', 'Not scored')}**

{fit_result.get('explanation', '')}

{_bullets(dimensions)}

## 3. Skill Match

### Matched Skills

{_bullets(fit_result.get('matched_skills', []))}

### Missing Skills

{_bullets(fit_result.get('missing_skills', []))}

## 4. Recommended Projects

{_bullets(projects)}

## 5. Resume Suggestions

### Keywords

{_bullets(resume_suggestions.get('matched_keywords', []))}

### Resume Bullet Suggestions

{_bullets(resume_suggestions.get('bullet_suggestions', []))}

## 6. Cover Letter Draft

{cover_letter.strip()}

## 7. Risk Flags

{_bullets(fit_result.get('risk_flags', []))}

## 8. Next Action Plan

1. Confirm the role requirements against the original listing.
2. Tailor the resume using only keywords supported by real evidence.
3. Edit the cover letter placeholders and verify every claim.
4. Record the opportunity in the local tracker before applying manually.

## 9. Safety Note

This local-first report is planning support, not hiring, legal, immigration, or professional advice. Apply manually, protect private data, and use only claims supported by real coursework, projects, or employment evidence.
"""

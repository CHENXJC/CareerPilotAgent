"""Transparent candidate-to-job fit scoring."""

from __future__ import annotations

from .utils import normalize_text


DIMENSION_MAX = {
    "Domain Fit": 15,
    "Skill Match": 25,
    "Portfolio Evidence": 20,
    "Experience Level Fit": 15,
    "Communication / Business Fit": 10,
    "Location / Work Mode Fit": 5,
    "Current Stage Suitability": 10,
}


def _project_matches(project: dict, job_terms: set[str]) -> int:
    evidence = " ".join([project.get("name", ""), project.get("description", ""), *project.get("skills", [])])
    normalized = normalize_text(evidence)
    return sum(1 for term in job_terms if normalize_text(term) in normalized)


def score_candidate_fit(job_data: dict, candidate_profile: dict) -> dict:
    job_skills = {normalize_text(item): item for item in job_data.get("skills", [])}
    candidate_skills = {normalize_text(item): item for item in candidate_profile.get("skills", [])}
    matched_keys = sorted(set(job_skills) & set(candidate_skills))
    missing_keys = sorted(set(job_skills) - set(candidate_skills))
    matched = [job_skills[key] for key in matched_keys]
    missing = [job_skills[key] for key in missing_keys]

    target_categories = {normalize_text(item) for item in candidate_profile.get("target_roles", [])}
    category = normalize_text(job_data.get("job_category", ""))
    domain_ratio = 1.0 if category in target_categories else (0.7 if category in {"general business", "administration", "operations"} else 0.45)
    skill_ratio = len(matched_keys) / max(1, len(job_skills))

    projects = candidate_profile.get("portfolio_projects", [])
    job_terms = set(job_skills) | {category}
    ranked = sorted(projects, key=lambda item: _project_matches(item, job_terms), reverse=True)
    recommended = [item["name"] for item in ranked if _project_matches(item, job_terms) > 0][:3]
    portfolio_ratio = min(1.0, sum(_project_matches(item, job_terms) for item in ranked[:3]) / max(2, len(job_terms)))

    seniority = job_data.get("seniority_level", "Unknown")
    experience_ratio = {"Internship": 1.0, "Entry Level": 1.0, "Junior": 0.82, "Unknown": 0.7, "Mid Level": 0.4, "Senior": 0.15}.get(seniority, 0.6)
    communication_ratio = 1.0 if "business communication" in candidate_skills else 0.65
    location = normalize_text(job_data.get("location", ""))
    profile_location = normalize_text(candidate_profile.get("location", ""))
    location_ratio = 1.0 if location in {"", "unknown"} or profile_location in location or "remote" in normalize_text(job_data.get("work_mode", "")) else 0.5
    stage_ratio = 1.0 if seniority in {"Internship", "Entry Level", "Junior"} else (0.7 if seniority == "Unknown" else 0.3)

    ratios = [domain_ratio, skill_ratio, portfolio_ratio, experience_ratio, communication_ratio, location_ratio, stage_ratio]
    dimension_scores = {
        name: round(max_points * ratio, 1)
        for (name, max_points), ratio in zip(DIMENSION_MAX.items(), ratios)
    }
    total = round(sum(dimension_scores.values()), 1)
    priority = "High Priority" if total >= 80 else "Good Fit" if total >= 65 else "Possible Fit" if total >= 50 else "Low Priority"

    risks: list[str] = []
    if seniority in {"Mid Level", "Senior"}:
        risks.append(f"The role is classified as {seniority}, above the demo candidate's current student stage.")
    if skill_ratio < 0.5 and job_skills:
        risks.append("Fewer than half of the detected job skills are evidenced in the selected profile.")
    if not recommended:
        risks.append("No portfolio project has strong keyword evidence for this role yet.")
    if not risks:
        risks.append("Rule-based scoring should be validated against the full job requirements before applying.")

    domain_note = (
        f"The {job_data.get('job_category', 'general business')} role appears aligned with the candidate's Business and Marketing background."
        if domain_ratio >= 0.7
        else "The role is outside the candidate's strongest Business and Marketing target areas, so domain fit is cautious."
    )
    evidence_note = (
        f"Relevant project evidence is available through {', '.join(recommended[:2])}."
        if recommended
        else "The profile does not yet show strong portfolio evidence for the detected requirements."
    )
    gap_note = (
        "The main gap is formal professional experience; the application should present portfolio work as project evidence, not employment."
        if seniority in {"Internship", "Entry Level", "Junior", "Unknown"}
        else "The requested experience level is a substantial gap for the current student profile."
    )
    stage_note = (
        f"This {seniority.lower()} role is suitable for a student or early-career application with targeted resume edits."
        if seniority in {"Internship", "Entry Level", "Junior"}
        else "Apply only if the responsibilities, supervision, and learning scope match the candidate's current stage."
    )
    explanation = " ".join(
        [
            f"Score: {total}/100 ({priority}). {len(matched)} of {len(job_skills)} detected skills are matched.",
            domain_note,
            evidence_note,
            gap_note,
            stage_note,
        ]
    )
    return {
        "profile_name": candidate_profile.get("profile_name", "Selected Profile"),
        "total_score": total,
        "priority_label": priority,
        "dimension_scores": dimension_scores,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommended_projects": recommended,
        "risk_flags": risks,
        "explanation": explanation,
    }

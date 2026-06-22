"""Template-based, evidence-conscious cover letter generator."""

from __future__ import annotations


def generate_cover_letter(job_data: dict, candidate_profile: dict, fit_result: dict) -> str:
    company = job_data.get("company_name") or "[Company Name]"
    role = job_data.get("role_title") or "[Role Title]"
    candidate_type = candidate_profile.get("candidate_type", candidate_profile.get("stage", "early-career candidate"))
    article = "an" if str(candidate_type).strip().lower().startswith(("a", "e", "i", "o", "u")) else "a"
    background_value = candidate_profile.get("background", "Business and Marketing")
    background = " and ".join(background_value) if isinstance(background_value, list) else str(background_value)
    projects = fit_result.get("recommended_projects", [])[:2]
    project_sentence = (
        f"Relevant portfolio work includes {', '.join(projects)}, where I practised building structured, explainable workflows."
        if projects
        else "My portfolio work has helped me practise structured analysis, dashboard development, and clear business communication."
    )
    skills = ", ".join(fit_result.get("matched_skills", [])[:5]) or "business analysis and communication"
    return f"""Dear Hiring Team,

I am writing to express my interest in the {role} opportunity at {company}. I am {article} {candidate_type} with a {background} background, seeking an opportunity to contribute while continuing to build practical experience.

The role is relevant to skills I have developed through coursework and portfolio projects, including {skills}. {project_sentence} These are project-based experiences rather than claims of full-time professional employment.

I would bring curiosity, careful communication, and a willingness to learn. I am particularly interested in understanding your team's priorities and supporting practical work with well-organised analysis and reliable follow-through.

Thank you for considering my application. I would welcome the opportunity to discuss how my current skills and learning mindset could support the team.

Kind regards,
[Your Name]
"""

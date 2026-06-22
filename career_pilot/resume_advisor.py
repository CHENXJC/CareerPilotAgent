"""Honest resume suggestions based on demo project evidence."""

from __future__ import annotations

from .utils import normalize_text, unique


def suggest_projects_to_highlight(job_data: dict, candidate_profile: dict) -> list[dict]:
    terms = {normalize_text(item) for item in job_data.get("skills", [])}
    terms.add(normalize_text(job_data.get("job_category", "")))
    scored: list[tuple[int, dict]] = []
    for project in candidate_profile.get("portfolio_projects", []):
        evidence = normalize_text(" ".join([project.get("name", ""), project.get("description", ""), *project.get("skills", [])]))
        score = sum(term in evidence for term in terms if term)
        scored.append((score, project))
    ranked = sorted(scored, key=lambda item: item[0], reverse=True)
    return [
        {"name": project["name"], "reason": project["description"], "evidence_type": "Portfolio project"}
        for score, project in ranked[:3]
        if score > 0
    ]


def generate_resume_keywords(job_data: dict, fit_result: dict) -> dict:
    return {
        "matched_keywords": unique(fit_result.get("matched_skills", []) + job_data.get("keywords", [])),
        "missing_keywords": fit_result.get("missing_skills", []),
        "usage_note": "Use a keyword only where the resume contains truthful project, coursework, or work evidence.",
    }


def generate_resume_bullets(job_data: dict, candidate_profile: dict, fit_result: dict) -> list[str]:
    projects = suggest_projects_to_highlight(job_data, candidate_profile)
    polished_project_bullets = {
        "MarketSenseAgent": "Built a market-data workflow to automate analysis, generate structured reports, and support recurring business insight reviews.",
        "QuantLabAgent": "Developed a quantitative research dashboard to compare strategies, review backtesting results, and communicate analytical findings.",
        "VideoExtractSkill": "Developed a local-first AI workflow to extract text from videos and images and convert the results into structured reports.",
        "SocialPainFinderAgent": "Created a social media pain-point discovery tool to classify user needs and convert insights into product opportunities.",
        "IdeaScoreAgent": "Built a Streamlit-based dashboard to score business ideas, explain each decision factor, and export actionable reports.",
    }
    bullets = [
        polished_project_bullets.get(
            item["name"],
            f"Built {item['name']}, a portfolio project that {item['reason'].rstrip('.').lower()}.",
        )
        for item in projects
    ]
    defaults = [
        "Built a Streamlit-based dashboard to analyse structured data, generate insights, and support decision-making workflows.",
        "Applied Python and data-analysis fundamentals to organise information, compare options, and produce clear business reports.",
        "Translated user and business needs into a focused workflow with documented inputs, outputs, and limitations.",
    ]
    return unique(bullets + defaults)[:5]


def build_resume_suggestions(job_data: dict, candidate_profile: dict, fit_result: dict) -> dict:
    keywords = generate_resume_keywords(job_data, fit_result)
    return {
        **keywords,
        "bullet_suggestions": generate_resume_bullets(job_data, candidate_profile, fit_result),
        "projects_to_highlight": suggest_projects_to_highlight(job_data, candidate_profile),
        "warning": "These are project-based suggestions. Do not relabel projects as paid employment or add unsupported metrics.",
    }

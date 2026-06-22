"""Explainable, local rule-based job description parser."""

from __future__ import annotations

import re

from .utils import normalize_text, unique


SKILLS = {
    "market research": ("market research", "market analysis"),
    "customer insight": ("customer insight", "consumer insight", "customer insights"),
    "marketing analysis": ("marketing analysis", "marketing analytics"),
    "content strategy": ("content strategy", "content planning"),
    "social media": ("social media",),
    "digital marketing": ("digital marketing",),
    "campaign management": ("campaign management", "marketing campaign"),
    "SEO": ("seo", "search engine optimization"),
    "Excel": ("excel", "spreadsheets"),
    "Python": ("python",),
    "SQL": ("sql",),
    "Power BI": ("power bi", "powerbi"),
    "Tableau": ("tableau",),
    "data analysis": ("data analysis", "data analytics", "analyse data", "analyze data"),
    "dashboard building": ("dashboard", "dashboards"),
    "requirements gathering": ("requirements gathering", "business requirements"),
    "process improvement": ("process improvement", "continuous improvement"),
    "stakeholder management": ("stakeholder management", "stakeholders"),
    "business communication": ("business communication", "written communication", "verbal communication"),
    "presentation": ("presentation", "presentations"),
    "reporting": ("reporting", "reports"),
    "project management": ("project management", "project coordination"),
    "customer service": ("customer service", "customer support"),
    "sales": ("sales", "business development"),
    "CRM": ("crm", "salesforce", "hubspot"),
    "administration": ("administration", "administrative"),
    "operations": ("operations", "operational"),
    "financial analysis": ("financial analysis", "financial modelling", "financial modeling"),
    "AI tools": ("ai tools", "artificial intelligence", "generative ai"),
    "automation": ("automation", "workflow automation"),
    "Streamlit": ("streamlit",),
}

CATEGORY_TERMS = {
    "Marketing": ("marketing", "campaign", "content", "brand", "seo", "social media"),
    "Business Analyst": ("business analyst", "requirements", "stakeholder", "process improvement"),
    "Data Analyst": ("data analyst", "analytics", "sql", "tableau", "power bi", "dashboard"),
    "Operations": ("operations", "logistics", "workflow", "process", "coordination"),
    "Administration": ("administration", "administrative", "office support", "scheduling"),
    "Sales": ("sales", "business development", "lead generation", "crm"),
    "Customer Support": ("customer support", "customer service", "client service"),
    "AI / Automation": ("automation", "artificial intelligence", "generative ai", "ai assistant"),
    "Finance / Investment": ("finance", "investment", "portfolio", "financial analysis"),
}


def extract_skills(text: str) -> list[str]:
    haystack = normalize_text(text)
    matches = [name for name, aliases in SKILLS.items() if any(alias in haystack for alias in aliases)]
    return sorted(matches, key=str.lower)


def detect_job_category(text: str) -> str:
    haystack = normalize_text(text)
    scores = {
        category: sum(haystack.count(term) for term in terms)
        for category, terms in CATEGORY_TERMS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] else "General Business"


def detect_seniority(text: str) -> str:
    haystack = normalize_text(text)
    ordered = (
        ("Internship", ("internship", "intern ", "student placement", "graduate intern")),
        ("Senior", ("senior", "lead ", "manager", "5+ years", "7+ years")),
        ("Entry Level", ("entry level", "entry-level", "graduate", "no experience required")),
        ("Junior", ("junior", "1-2 years", "one to two years")),
        ("Mid Level", ("mid level", "mid-level", "3+ years", "3-5 years")),
    )
    for label, terms in ordered:
        if any(term in haystack for term in terms):
            return label
    return "Unknown"


def extract_keywords(text: str) -> list[str]:
    skills = extract_skills(text)
    haystack = normalize_text(text)
    extras = [
        term
        for term in ("communication", "teamwork", "problem solving", "attention to detail", "melbourne", "remote", "hybrid")
        if term in haystack
    ]
    return unique(skills + extras)[:20]


def _extract_title(lines: list[str]) -> str:
    for line in lines[:8]:
        match = re.match(r"(?:role|position|job title)\s*:\s*([^|\n]+)", line, re.I)
        if match:
            return match.group(1).strip()
    for line in lines[:4]:
        if 2 <= len(line.split()) <= 8 and not re.match(r"(?:company|location)\s*:", line, re.I):
            return line.strip("# -*")
    return "[Role Title]"


def _extract_company(lines: list[str], text: str) -> str:
    match = re.search(r"(?:company|organisation|organization)\s*:\s*([^\n|]+)", text, re.I)
    if match:
        return match.group(1).strip()
    for line in lines[:8]:
        match = re.search(r"\bat\s+([A-Z][A-Za-z0-9 &.-]{2,40})", line)
        if match:
            return match.group(1).strip(" .")
    return "[Company Name]"


def _extract_responsibilities(text: str) -> list[str]:
    candidates: list[str] = []
    action_terms = ("support", "assist", "analyse", "analyze", "create", "manage", "coordinate", "prepare", "develop", "maintain", "research", "report")
    for raw in text.splitlines():
        line = raw.strip(" \t-*•")
        if len(line) >= 20 and any(re.search(rf"\b{term}\w*\b", line, re.I) for term in action_terms):
            candidates.append(line)
    return unique(candidates)[:8]


def parse_job_description(text: str) -> dict:
    if not isinstance(text, str):
        raise TypeError("Job description must be a string")
    cleaned = text.strip()
    if not cleaned:
        return {
            "role_title": "[Role Title]", "company_name": "[Company Name]",
            "responsibilities": [], "required_skills": [], "preferred_skills": [],
            "skills": [], "keywords": [], "seniority_level": "Unknown",
            "job_category": "General Business", "location": "Unknown", "work_mode": "Unknown",
        }
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    skills = extract_skills(cleaned)
    preferred_blocks = " ".join(line for line in lines if re.search(r"preferred|desirable|nice to have", line, re.I))
    preferred = extract_skills(preferred_blocks)
    required = [skill for skill in skills if skill not in preferred]
    location_match = re.search(r"location\s*:\s*([^\n|]+)", cleaned, re.I)
    lower = normalize_text(cleaned)
    work_mode = next((mode.title() for mode in ("remote", "hybrid", "on-site", "onsite") if mode in lower), "Unknown")
    return {
        "role_title": _extract_title(lines),
        "company_name": _extract_company(lines, cleaned),
        "responsibilities": _extract_responsibilities(cleaned),
        "required_skills": required,
        "preferred_skills": preferred,
        "skills": skills,
        "keywords": extract_keywords(cleaned),
        "seniority_level": detect_seniority(cleaned),
        "job_category": detect_job_category(cleaned),
        "location": location_match.group(1).strip() if location_match else ("Melbourne" if "melbourne" in lower else "Unknown"),
        "work_mode": "On-site" if work_mode == "Onsite" else work_mode,
    }

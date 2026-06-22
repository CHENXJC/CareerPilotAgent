from career_pilot.cover_letter import generate_cover_letter
from career_pilot.fit_scorer import score_candidate_fit
from career_pilot.jd_parser import parse_job_description
from career_pilot.report_builder import build_markdown_report
from career_pilot.resume_advisor import build_resume_suggestions
from career_pilot.sample_profile import load_sample_profile


def test_report_contains_required_sections():
    profile = load_sample_profile()
    job = parse_job_description("Role: Business Analyst Intern\nInternship using Excel, requirements gathering, process improvement, and reporting.")
    fit = score_candidate_fit(job, profile)
    suggestions = build_resume_suggestions(job, profile, fit)
    letter = generate_cover_letter(job, profile, fit)
    report = build_markdown_report(job, fit, suggestions, letter)
    for section in ("Job Summary", "Fit Score", "Resume Bullet Suggestions", "Cover Letter Draft"):
        assert section in report

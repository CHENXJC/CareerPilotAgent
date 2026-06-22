from career_pilot.fit_scorer import score_candidate_fit
from career_pilot.jd_parser import parse_job_description
from career_pilot.resume_advisor import generate_resume_bullets
from career_pilot.sample_profile import load_sample_profile


def test_generates_three_realistic_bullets():
    profile = load_sample_profile()
    job = parse_job_description("Marketing Assistant internship with market research, customer insight, Excel, and data analysis.")
    result = score_candidate_fit(job, profile)
    bullets = generate_resume_bullets(job, profile, result)
    assert len(bullets) >= 3
    joined = " ".join(bullets).lower()
    assert "worked full-time" not in joined
    assert "years of professional experience" not in joined

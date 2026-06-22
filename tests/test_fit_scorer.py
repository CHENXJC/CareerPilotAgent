from career_pilot.fit_scorer import score_candidate_fit
from career_pilot.jd_parser import parse_job_description
from career_pilot.sample_profile import load_sample_profile


def _result():
    job = parse_job_description("Role: Marketing Intern\nMarketing internship using market research, Excel, data analysis, social media, and communication.")
    return score_candidate_fit(job, load_sample_profile())


def test_score_is_bounded():
    assert 0 <= _result()["total_score"] <= 100


def test_returns_priority_and_dimensions():
    result = _result()
    assert result["priority_label"] in {"High Priority", "Good Fit", "Possible Fit", "Low Priority"}
    assert len(result["dimension_scores"]) == 7


def test_returns_matched_and_missing_skills():
    result = _result()
    assert isinstance(result["matched_skills"], list)
    assert isinstance(result["missing_skills"], list)

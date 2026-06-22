from career_pilot.jd_parser import extract_skills, parse_job_description


MARKETING_JD = """Role: Marketing Assistant
Company: Demo Studio
Location: Melbourne
Entry-level role supporting market research, customer insight, social media, Excel analysis, reporting, and content strategy.
Assist with campaign reporting and analyse customer feedback.
"""


def test_parser_returns_dict():
    assert isinstance(parse_job_description(MARKETING_JD), dict)


def test_detects_marketing_category():
    assert parse_job_description(MARKETING_JD)["job_category"] == "Marketing"


def test_extracts_at_least_three_skills():
    assert len(extract_skills(MARKETING_JD)) >= 3


def test_pipe_delimited_title_stops_at_separator():
    parsed = parse_job_description("Role: Marketing Assistant | Company: Demo Studio | Location: Melbourne")
    assert parsed["role_title"] == "Marketing Assistant"

"""CareerPilotAgent CAREER-002 Streamlit dashboard."""

from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from career_pilot.cover_letter import generate_cover_letter
from career_pilot.fit_scorer import DIMENSION_MAX, score_candidate_fit
from career_pilot.jd_parser import parse_job_description
from career_pilot.profile_manager import (
    PRIVACY_NOTE,
    build_private_profile_template,
    create_private_profile_from_sample,
    get_active_profile,
    load_private_profile,
    load_sample_profile,
    private_profile_exists,
    save_private_profile,
)
from career_pilot.report_builder import build_markdown_report
from career_pilot.resume_advisor import build_resume_suggestions
from career_pilot.tracker import DEFAULT_STATUSES, add_application, load_tracker, save_tracker
from career_pilot.utils import safe_filename


ROOT = Path(__file__).resolve().parent
SAMPLE_JOBS_PATH = ROOT / "data" / "sample_jobs.csv"
TRACKER_PATH = ROOT / "data" / "application_tracker.csv"

PRIORITY_GUIDANCE = {
    "High Priority": "Apply soon and tailor the resume to the strongest evidence.",
    "Good Fit": "Worth applying with targeted resume edits.",
    "Possible Fit": "Apply only if the role aligns with your goals and learning plan.",
    "Low Priority": "Deprioritise unless there is a clear strategic reason to apply.",
}

PROFILE_RESULT_KEYS = ("job_data", "fit_result", "resume_suggestions", "cover_draft", "report")


def render_tags(items: list[str], empty: str = "None detected") -> None:
    """Render compact, escaped keyword tags."""
    if not items:
        st.caption(empty)
        return
    tags = "".join(f'<span class="cp-tag">{escape(item)}</span>' for item in items)
    st.markdown(f'<div class="cp-tags">{tags}</div>', unsafe_allow_html=True)


def lines_to_list(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def list_to_lines(items: object) -> str:
    if isinstance(items, list):
        return "\n".join(str(item) for item in items)
    return str(items or "")


def projects_to_lines(projects: object) -> str:
    lines: list[str] = []
    for project in projects if isinstance(projects, list) else []:
        if isinstance(project, dict):
            skills = ", ".join(project.get("skills", []))
            lines.append(f"{project.get('name', '')} | {project.get('description', '')} | {skills}".rstrip(" |"))
        else:
            lines.append(str(project))
    return "\n".join(lines)


def parse_project_lines(value: str) -> list[dict]:
    projects: list[dict] = []
    for line in lines_to_list(value):
        parts = [part.strip() for part in line.split("|", 2)]
        projects.append(
            {
                "name": parts[0],
                "description": parts[1] if len(parts) > 1 else "",
                "skills": [item.strip() for item in parts[2].split(",") if item.strip()] if len(parts) > 2 else [],
            }
        )
    return projects


def clear_analysis_results() -> None:
    for key in PROFILE_RESULT_KEYS:
        st.session_state.pop(key, None)


def clear_profile_widgets() -> None:
    st.session_state.profile_editor_version = st.session_state.get("profile_editor_version", 0) + 1


st.set_page_config(page_title="CareerPilotAgent", page_icon=":material/explore:", layout="wide")
st.markdown(
    """<style>
    .block-container {max-width: 1180px; padding-top: 1.6rem; padding-bottom: 3rem;}
    .cp-hero {padding: 1.5rem 1.6rem; border: 1px solid #dbe3ec; border-radius: 18px;
              background: linear-gradient(135deg, #f7fbff 0%, #f7f5ff 100%); margin-bottom: 1rem;}
    .cp-hero h1 {margin: 0 0 .25rem 0; font-size: 2.25rem;}
    .cp-hero p {margin: 0; color: #465568; font-size: 1.05rem;}
    .cp-badge {display: inline-block; margin: .7rem .35rem 0 0; padding: .35rem .65rem;
               border-radius: 999px; background: #e8f1ff; color: #174c8f; font-weight: 600; font-size: .86rem;}
    .cp-safety {margin-top: .8rem; padding: .65rem .8rem; border-left: 4px solid #2f7d5b;
                background: #f1faf6; color: #285844; border-radius: 6px;}
    [data-testid="stMetric"] {border: 1px solid #dfe5ec; border-radius: 12px; padding: .8rem; background: #fff;}
    .cp-tags {display: flex; flex-wrap: wrap; gap: .4rem; margin: .35rem 0 .85rem;}
    .cp-tag {padding: .25rem .55rem; border-radius: 999px; background: #edf3f8; border: 1px solid #d7e1ea;
             font-size: .84rem;}
    .cp-copy {padding: .8rem 1rem; border: 1px solid #dfe5ec; border-radius: 10px; background: #f8fafc;
              margin-bottom: .55rem;}
    </style>""",
    unsafe_allow_html=True,
)

demo_profile = load_sample_profile()
sample_jobs = pd.read_csv(SAMPLE_JOBS_PATH)
st.session_state.setdefault("jd_input", "")
st.session_state.setdefault("last_profile_mode", "Demo Profile")

with st.sidebar:
    st.header("CareerPilotAgent")
    st.success("Current checkpoint: CAREER-005")
    st.caption("Local-first portfolio MVP")
    profile_mode = st.radio(
        "Profile mode",
        ["Demo Profile", "Local Private Profile"],
        help="Demo Profile is public-safe. Local Private Profile is stored only in data/private/.",
    )
    if profile_mode != st.session_state.last_profile_mode:
        clear_analysis_results()
        st.session_state.last_profile_mode = profile_mode
    local_profile_available = private_profile_exists()
    if profile_mode == "Demo Profile":
        st.caption("Safe sample data for the public GitHub showcase.")
        st.markdown(f"**Active:** {demo_profile['profile_name']}")
    elif not local_profile_available:
        st.warning("No local private profile found.")
        if st.button("Create Local Private Profile from Demo", width="stretch"):
            create_private_profile_from_sample(demo_profile)
            clear_profile_widgets()
            clear_analysis_results()
            st.session_state.profile_notice = "Local private profile created from the safe demo template."
            st.rerun()
    else:
        st.caption("Editable local profile. Stored in data/private/ and ignored by Git.")
        st.markdown(f"**Active:** {load_private_profile().get('profile_name', 'Local Private Profile')}")
    st.selectbox(
        "Target role",
        ["Marketing", "Business Analyst", "Data Analyst", "Operations", "Admin", "AI Automation Assistant"],
    )
    st.divider()
    st.subheader("Sample job descriptions")
    if st.button("Load sample Marketing JD", width="stretch"):
        st.session_state.jd_input = sample_jobs.loc[
            sample_jobs["role"] == "Marketing Assistant", "job_description"
        ].iloc[0]
    if st.button("Load sample Business Analyst JD", width="stretch"):
        st.session_state.jd_input = sample_jobs.loc[
            sample_jobs["role"] == "Business Analyst Intern", "job_description"
        ].iloc[0]
    if st.button("Clear input and results", width="stretch"):
        st.session_state.jd_input = ""
        clear_analysis_results()
    st.divider()
    st.subheader("Quick workflow")
    st.markdown(
        "1. Paste or load a JD\n"
        "2. Analyse fit\n"
        "3. Review resume suggestions\n"
        "4. Edit the cover letter\n"
        "5. Save to the tracker\n"
        "6. Export the report"
    )

active_profile = get_active_profile(profile_mode)
local_profile_available = private_profile_exists()

st.markdown(
    """<section class="cp-hero">
      <h1>CareerPilotAgent</h1>
      <p>AI Job Matching &amp; Application Assistant for international business students.</p>
      <div>
        <span class="cp-badge">JD Analyzer</span>
        <span class="cp-badge">Fit Score</span>
        <span class="cp-badge">Resume &amp; Cover Letter Assistant</span>
      </div>
      <div class="cp-safety">Local-first demo. No auto-apply. No scraping. No private resume data required.</div>
    </section>""",
    unsafe_allow_html=True,
)

profile_tab, analyzer_tab, fit_tab, resume_tab, cover_tab, tracker_tab, export_tab = st.tabs(
    ["1. Profile", "2. JD Analyzer", "3. Fit Score", "4. Resume Suggestions", "5. Cover Letter", "6. Application Tracker", "7. Export Report"]
)

with profile_tab:
    st.header("Candidate Profile")
    if notice := st.session_state.pop("profile_notice", None):
        st.success(notice)
    if profile_mode == "Demo Profile":
        st.info("This is safe demo data for public showcase. It does not contain private resume information.")
        left, right = st.columns(2)
        left.metric("Profile", demo_profile.get("profile_name", "Demo Profile"))
        right.metric("Location", demo_profile.get("location", "Not specified"))
        background = demo_profile.get("background", [])
        st.markdown("**Background**")
        st.write(" / ".join(background) if isinstance(background, list) else background)
        st.markdown("**Target roles**")
        render_tags(demo_profile.get("target_roles", []))
        st.markdown("**Skills**")
        render_tags(demo_profile.get("skills", []))
        st.markdown("**Portfolio projects**")
        for project in demo_profile.get("portfolio_projects", []):
            with st.container(border=True):
                st.markdown(f"**{project.get('name', 'Project')}**")
                st.write(project.get("description", ""))
        st.caption(demo_profile.get("privacy_note", "Synthetic public demo data."))
    elif not local_profile_available:
        st.warning("No local private profile found.")
        st.write("Use the sidebar button to create an editable local profile from the public-safe demo template.")
    else:
        local_profile = load_private_profile()
        editor_version = st.session_state.setdefault("profile_editor_version", 0)
        widget_key = lambda name: f"{name}_{editor_version}"
        st.warning(
            "Do not store phone numbers, passport or visa numbers, student IDs, exact home addresses, passwords, or private contact details."
        )
        st.caption("The file is ignored by Git, but highly sensitive information still does not belong here.")
        with st.form("private_profile_editor"):
            c1, c2 = st.columns(2)
            profile_name = c1.text_input(
                "Profile name", value=local_profile.get("profile_name", "Local Private Profile"), key=widget_key("private_name")
            )
            candidate_type = c2.text_input(
                "Candidate type", value=local_profile.get("candidate_type", ""), key=widget_key("private_candidate_type")
            )
            background = c1.text_input(
                "Background", value=local_profile.get("background", ""), key=widget_key("private_background")
            )
            location = c2.text_input("Location", value=local_profile.get("location", ""), key=widget_key("private_location"))
            target_roles = st.text_area(
                "Target roles — one per line", value=list_to_lines(local_profile.get("target_roles", [])), key=widget_key("private_target_roles")
            )
            skills = st.text_area(
                "Skills — one per line", value=list_to_lines(local_profile.get("skills", [])), key=widget_key("private_skills")
            )
            tools = st.text_area(
                "Tools — one per line", value=list_to_lines(local_profile.get("tools", [])), key=widget_key("private_tools")
            )
            projects = st.text_area(
                "Portfolio projects — Name | Description | skill 1, skill 2",
                value=projects_to_lines(local_profile.get("portfolio_projects", [])),
                key=widget_key("private_projects"),
                height=180,
            )
            availability = st.text_input(
                "Work availability", value=local_profile.get("work_availability", ""), key=widget_key("private_availability"),
                placeholder="For example: part-time, internship, entry-level, casual work",
            )
            preferred_locations = st.text_area(
                "Preferred locations — one per line",
                value=list_to_lines(local_profile.get("preferred_locations", [])),
                key=widget_key("private_locations"),
            )
            strengths = st.text_area(
                "Strengths — one per line", value=list_to_lines(local_profile.get("strengths", [])), key=widget_key("private_strengths")
            )
            experience_notes = st.text_area(
                "Experience notes", value=local_profile.get("experience_notes", ""), key=widget_key("private_experience")
            )
            career_goals = st.text_area(
                "Career goals", value=local_profile.get("career_goals", ""), key=widget_key("private_goals")
            )
            save_profile = st.form_submit_button("Save Local Profile", type="primary", width="stretch")
            if save_profile:
                updated_profile = {
                    "profile_name": profile_name.strip() or "Local Private Profile",
                    "candidate_type": candidate_type.strip(),
                    "background": background.strip(),
                    "location": location.strip(),
                    "target_roles": lines_to_list(target_roles),
                    "skills": lines_to_list(skills),
                    "tools": lines_to_list(tools),
                    "portfolio_projects": parse_project_lines(projects),
                    "work_availability": availability.strip(),
                    "preferred_locations": lines_to_list(preferred_locations),
                    "strengths": lines_to_list(strengths),
                    "experience_notes": experience_notes.strip(),
                    "career_goals": career_goals.strip(),
                    "privacy_note": PRIVACY_NOTE,
                }
                save_private_profile(updated_profile)
                clear_analysis_results()
                st.session_state.profile_notice = "Local private profile saved. Future analyses will use it."
                st.rerun()
        reset_col, reload_col = st.columns(2)
        if reset_col.button("Reset from Demo Profile", width="stretch"):
            create_private_profile_from_sample(demo_profile)
            clear_profile_widgets()
            clear_analysis_results()
            st.session_state.profile_notice = "Local profile reset from the safe demo template."
            st.rerun()
        if reload_col.button("Reload Local Profile", width="stretch"):
            clear_profile_widgets()
            clear_analysis_results()
            st.session_state.profile_notice = "Local profile reloaded from disk."
            st.rerun()

with analyzer_tab:
    st.header("Job Description Analyzer")
    st.write("Paste the full listing for better title, category, seniority, skill, and responsibility detection.")
    jd_text = st.text_area(
        "Job description",
        key="jd_input",
        height=280,
        placeholder="Paste a job description or load a sample JD to begin.",
    )
    if not jd_text.strip():
        st.info("Paste a job description or load a sample JD to begin.")
    analysis_blocked = profile_mode == "Local Private Profile" and not local_profile_available
    if analysis_blocked:
        st.warning("Create the local private profile before analysing with this profile mode.")
    if st.button("Analyze Job Description", type="primary", width="stretch", disabled=analysis_blocked):
        if not jd_text.strip():
            st.warning("Please paste or load a job description first.")
        else:
            job_data = parse_job_description(jd_text)
            fit_result = score_candidate_fit(job_data, active_profile)
            suggestions = build_resume_suggestions(job_data, active_profile, fit_result)
            letter = generate_cover_letter(job_data, active_profile, fit_result)
            st.session_state.update(
                job_data=job_data,
                fit_result=fit_result,
                resume_suggestions=suggestions,
                cover_draft=letter,
                report=build_markdown_report(job_data, fit_result, suggestions, letter),
            )
            st.success("Local analysis complete. Continue through the tabs to review the evidence.")
    if "job_data" in st.session_state:
        job = st.session_state.job_data
        st.subheader("Extracted job summary")
        cols = st.columns(4)
        cols[0].metric("Category", job["job_category"])
        cols[1].metric("Seniority", job["seniority_level"])
        cols[2].metric("Company", job["company_name"])
        cols[3].metric("Work mode", job["work_mode"])
        st.markdown("**Detected skills**")
        render_tags(job["skills"])
        st.markdown("**Search and resume keywords**")
        render_tags(job["keywords"])
        with st.expander("Responsibilities summary", expanded=True):
            for item in job["responsibilities"] or ["No action-oriented responsibility lines detected."]:
                st.markdown(f"- {item}")

with fit_tab:
    st.header("Candidate–Job Fit")
    if "fit_result" not in st.session_state:
        st.info("Analyse a job description to see the score, evidence, and gaps.")
    else:
        result = st.session_state.fit_result
        score_col, priority_col = st.columns([1, 1])
        score_col.metric("Overall fit score", f"{result['total_score']}/100")
        priority_col.metric("Application priority", result["priority_label"])
        st.info(PRIORITY_GUIDANCE[result["priority_label"]])
        st.subheader("Why this score?")
        st.write(result["explanation"])
        st.subheader("Dimension scorecards")
        dimensions = list(result["dimension_scores"].items())
        for start in range(0, len(dimensions), 4):
            row = st.columns(min(4, len(dimensions) - start))
            for column, (name, value) in zip(row, dimensions[start : start + 4]):
                maximum = DIMENSION_MAX[name]
                column.metric(name, f"{value}/{maximum}")
                column.progress(value / maximum)
        matched_col, missing_col = st.columns(2)
        with matched_col:
            st.subheader("Matched skills")
            render_tags(result["matched_skills"], "No direct skill match detected")
        with missing_col:
            st.subheader("Missing skills")
            if result["missing_skills"]:
                for skill in result["missing_skills"]:
                    st.warning(skill)
            else:
                st.success("No detected skill gaps in this listing.")
        st.subheader("Honest risk notes")
        for flag in result["risk_flags"]:
            st.warning(flag)

with resume_tab:
    st.header("Resume Suggestions")
    if "resume_suggestions" not in st.session_state:
        st.info("Analyse a job description to generate evidence-based resume suggestions.")
    else:
        suggestions = st.session_state.resume_suggestions
        st.subheader("1. Keywords to include")
        render_tags(suggestions["matched_keywords"])
        st.caption(suggestions["usage_note"])
        st.subheader("2. Missing keywords to build")
        render_tags(suggestions["missing_keywords"], "No missing keywords detected")
        st.subheader("3. Suggested resume bullets")
        st.caption("Copy, edit, and keep only statements supported by your actual project evidence.")
        for bullet in suggestions["bullet_suggestions"]:
            st.markdown(f'<div class="cp-copy">• {escape(bullet)}</div>', unsafe_allow_html=True)
        st.subheader("4. Portfolio projects to highlight")
        for project in suggestions["projects_to_highlight"]:
            with st.container(border=True):
                st.markdown(f"**{project['name']}** · {project['evidence_type']}")
                st.write(project["reason"])
        st.subheader("5. Do not overclaim")
        st.warning(suggestions["warning"])

with cover_tab:
    st.header("Cover Letter Draft")
    st.info("This is an editable starting point, not final legal, immigration, recruitment, or professional advice.")
    if "cover_draft" not in st.session_state:
        st.info("Analyse a job description to create a draft.")
    else:
        draft = st.text_area("Editable draft", key="cover_draft", height=430)
        left, right = st.columns([1, 2])
        left.download_button(
            "Download cover letter TXT", draft, "cover_letter_draft.txt", "text/plain", width="stretch"
        )
        right.caption("Replace placeholders, check the employer name, and verify every claim before use.")
        with st.expander("Copy-ready preview", expanded=False):
            st.markdown(draft)

with tracker_tab:
    st.header("Application Tracker")
    st.caption("Store application planning only. Do not add private contact details, visa records, or employer correspondence.")
    tracker = load_tracker(str(TRACKER_PATH))
    current_job = st.session_state.get("job_data", {})
    current_fit = st.session_state.get("fit_result", {})
    with st.form("add_application_form", clear_on_submit=True):
        st.subheader("Add an application")
        c1, c2 = st.columns(2)
        company = c1.text_input(
            "Company", value=current_job.get("company_name", "") if current_job.get("company_name") != "[Company Name]" else ""
        )
        role = c2.text_input(
            "Role", value=current_job.get("role_title", "") if current_job.get("role_title") != "[Role Title]" else ""
        )
        status = c1.selectbox("Status", DEFAULT_STATUSES)
        next_action = c2.text_input("Next action", value="Tailor resume and apply manually")
        notes = st.text_area("Notes", placeholder="Keep notes brief and non-sensitive.")
        submitted = st.form_submit_button("Save application", width="stretch")
        if submitted:
            if not company.strip() or not role.strip():
                st.warning("Company and role are required. Nothing was saved.")
            else:
                tracker = add_application(
                    tracker,
                    company,
                    role,
                    current_job.get("job_category", "General Business"),
                    current_fit.get("total_score", 0),
                    current_fit.get("priority_label", "Not scored"),
                    status,
                    next_action,
                    notes,
                )
                save_tracker(tracker, str(TRACKER_PATH))
                st.success("Application saved locally.")
                st.rerun()
    st.subheader("Tracked applications")
    if tracker.empty:
        st.info("No applications saved yet.")
    else:
        st.dataframe(tracker, width="stretch", hide_index=True)
    st.download_button(
        "Download tracker CSV", tracker.to_csv(index=False), "application_tracker.csv", "text/csv", width="stretch"
    )

with export_tab:
    st.header("Export Analysis Report")
    if "fit_result" not in st.session_state:
        st.info("Analyse a job description to generate the report preview.")
    else:
        report = build_markdown_report(
            st.session_state.job_data,
            st.session_state.fit_result,
            st.session_state.resume_suggestions,
            st.session_state.cover_draft,
        )
        st.session_state.report = report
        st.caption("Preview the complete evidence-based report before downloading it.")
        with st.container(border=True):
            st.markdown(report)
        filename = safe_filename(st.session_state.job_data.get("role_title", "career_report")) + ".md"
        st.download_button(
            "Download Markdown report", report, filename, "text/markdown", width="stretch"
        )

st.divider()
st.caption(
    "CareerPilotAgent is not an auto-apply bot or resume fraud tool. It uses local, explainable rules; users remain responsible for every claim and application."
)

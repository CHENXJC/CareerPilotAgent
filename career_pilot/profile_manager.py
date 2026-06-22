"""Privacy-first profile loading and local JSON persistence."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path


PRIVATE_PROFILE_DIR = "data/private"
PRIVATE_PROFILE_PATH = "data/private/user_profile.json"
SAMPLE_PROFILE_PATH = "data/sample_profile.json"
PRIVACY_NOTE = "This file is stored locally and should not be committed to GitHub."


def ensure_private_profile_dir() -> None:
    """Create the default private profile directory when it is missing."""
    Path(PRIVATE_PROFILE_DIR).mkdir(parents=True, exist_ok=True)


def load_sample_profile(path: str = SAMPLE_PROFILE_PATH) -> dict:
    """Load the public-safe demo profile."""
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def private_profile_exists(path: str = PRIVATE_PROFILE_PATH) -> bool:
    return Path(path).is_file()


def _background_text(value: object) -> str:
    if isinstance(value, list):
        return " / ".join(str(item) for item in value)
    return str(value or "")


def build_private_profile_template(sample_profile: dict | None = None) -> dict:
    """Build a safe editable schema, optionally seeded from demo data."""
    sample = deepcopy(sample_profile) if sample_profile is not None else {}
    location = str(sample.get("location", ""))
    work_types = sample.get("target_work_types", [])
    return {
        "profile_name": "Local Private Profile",
        "candidate_type": sample.get("candidate_type", sample.get("stage", "International undergraduate student")),
        "background": _background_text(sample.get("background", "Business / Marketing")),
        "location": location,
        "target_roles": list(sample.get("target_roles", [])),
        "skills": list(sample.get("skills", [])),
        "tools": list(sample.get("tools", [])),
        "portfolio_projects": deepcopy(sample.get("portfolio_projects", [])),
        "work_availability": ", ".join(work_types) if isinstance(work_types, list) else str(work_types or ""),
        "preferred_locations": [location] if location else [],
        "strengths": list(sample.get("strengths", [])),
        "experience_notes": "Portfolio and coursework experience only; verify all claims before use.",
        "career_goals": "",
        "privacy_note": PRIVACY_NOTE,
    }


def save_private_profile(profile: dict, path: str = PRIVATE_PROFILE_PATH) -> None:
    """Persist a private profile as readable UTF-8 JSON."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = deepcopy(profile)
    payload["privacy_note"] = PRIVACY_NOTE
    with output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def create_private_profile_from_sample(
    sample_profile: dict, path: str = PRIVATE_PROFILE_PATH
) -> dict:
    profile = build_private_profile_template(sample_profile)
    save_private_profile(profile, path)
    return profile


def load_private_profile(path: str = PRIVATE_PROFILE_PATH) -> dict:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(
            f"Local private profile not found at {source}. Create it from the demo profile first."
        )
    with source.open("r", encoding="utf-8") as handle:
        profile = json.load(handle)
    return profile


def get_active_profile(profile_mode: str) -> dict:
    if profile_mode == "Demo Profile":
        return load_sample_profile()
    if profile_mode == "Local Private Profile":
        if private_profile_exists():
            return load_private_profile()
        profile = build_private_profile_template(load_sample_profile())
        profile["_profile_missing"] = True
        return profile
    raise ValueError("profile_mode must be 'Demo Profile' or 'Local Private Profile'")

from career_pilot.profile_manager import (
    PRIVACY_NOTE,
    build_private_profile_template,
    create_private_profile_from_sample,
    load_private_profile,
    private_profile_exists,
    save_private_profile,
)


def test_template_is_dict_with_required_keys():
    template = build_private_profile_template()
    assert isinstance(template, dict)
    for key in ("profile_name", "skills", "portfolio_projects", "privacy_note"):
        assert key in template


def test_save_and_load_private_profile(tmp_path):
    path = tmp_path / "private" / "profile.json"
    profile = build_private_profile_template()
    profile["skills"] = ["market research", "Excel"]
    save_private_profile(profile, path)
    loaded = load_private_profile(path)
    assert loaded["skills"] == ["market research", "Excel"]
    assert loaded["privacy_note"] == PRIVACY_NOTE


def test_private_profile_exists_tracks_file(tmp_path):
    path = tmp_path / "user_profile.json"
    assert not private_profile_exists(path)
    save_private_profile(build_private_profile_template(), path)
    assert private_profile_exists(path)


def test_create_from_sample_creates_json_with_privacy_note(tmp_path):
    path = tmp_path / "private" / "user_profile.json"
    sample = {
        "location": "Demo City",
        "skills": ["Excel"],
        "portfolio_projects": [],
        "target_roles": ["Marketing"],
    }
    profile = create_private_profile_from_sample(sample, path)
    assert path.is_file()
    assert profile["privacy_note"] == PRIVACY_NOTE
    assert load_private_profile(path)["privacy_note"] == PRIVACY_NOTE

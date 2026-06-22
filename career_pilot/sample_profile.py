"""Backward-compatible safe demo profile loader."""

from __future__ import annotations

from pathlib import Path

from .profile_manager import load_sample_profile as _load_sample_profile


DEFAULT_PROFILE_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_profile.json"


def load_sample_profile(path: str | Path = DEFAULT_PROFILE_PATH) -> dict:
    """Load the public demo profile. It contains no real personal data."""
    return _load_sample_profile(str(path))

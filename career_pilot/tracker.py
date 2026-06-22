"""CSV-backed local application tracker."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from .utils import ensure_parent


TRACKER_COLUMNS = ["date_added", "company", "role", "job_category", "fit_score", "priority", "status", "next_action", "notes"]
DEFAULT_STATUSES = ["Interested", "Applied", "Interview", "Rejected", "Offer", "Archived"]


def load_tracker(path: str = "data/application_tracker.csv") -> pd.DataFrame:
    source = Path(path)
    if not source.exists() or source.stat().st_size == 0:
        return pd.DataFrame(columns=TRACKER_COLUMNS)
    frame = pd.read_csv(source)
    for column in TRACKER_COLUMNS:
        if column not in frame:
            frame[column] = ""
    return frame[TRACKER_COLUMNS]


def add_application(
    df: pd.DataFrame,
    company: str,
    role: str,
    job_category: str,
    fit_score: float,
    priority: str,
    status: str = "Interested",
    next_action: str = "Review and tailor application",
    notes: str = "",
    date_added: str | None = None,
) -> pd.DataFrame:
    row = {
        "date_added": date_added or date.today().isoformat(), "company": company.strip(), "role": role.strip(),
        "job_category": job_category, "fit_score": fit_score, "priority": priority,
        "status": status if status in DEFAULT_STATUSES else "Interested", "next_action": next_action.strip(), "notes": notes.strip(),
    }
    new_row = pd.DataFrame([row], columns=TRACKER_COLUMNS)
    if df.empty:
        return new_row
    return pd.concat([df, new_row], ignore_index=True)


def save_tracker(df: pd.DataFrame, path: str = "data/application_tracker.csv") -> None:
    output = ensure_parent(path)
    df.reindex(columns=TRACKER_COLUMNS).to_csv(output, index=False)

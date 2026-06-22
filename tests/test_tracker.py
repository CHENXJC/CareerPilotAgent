import pandas as pd

from career_pilot.tracker import TRACKER_COLUMNS, add_application, load_tracker, save_tracker


def test_tracker_add_save_and_reload(tmp_path):
    tracker = pd.DataFrame(columns=TRACKER_COLUMNS)
    tracker = add_application(
        tracker,
        company="Demo Company",
        role="Marketing Intern",
        job_category="Marketing",
        fit_score=75,
        priority="Good Fit",
    )
    output = tmp_path / "tracker.csv"
    save_tracker(tracker, output)
    loaded = load_tracker(output)
    assert len(loaded) == 1
    assert loaded.iloc[0]["company"] == "Demo Company"

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from educasual.config import AnalysisConfig
from educasual.data.io import OULADTables
from educasual.features.definitions import add_analysis_variables


def _build_student_course_id(df: pd.DataFrame) -> pd.Series:
    return (
        df["id_student"].astype(str)
        + "::"
        + df["code_module"].astype(str)
        + "::"
        + df["code_presentation"].astype(str)
    )


def _coalesce_event_day(df: pd.DataFrame) -> pd.Series:
    return df["date"].where(df["date"].notna(), df["date_submitted"])


def _aggregate_daily_clicks(student_vle: pd.DataFrame) -> pd.DataFrame:
    vle = student_vle.copy()
    vle["student_course_id"] = _build_student_course_id(vle)
    grouped = (
        vle.groupby(["student_course_id", "date"], as_index=False)["sum_click"]
        .sum()
        .sort_values(["student_course_id", "date"])
    )
    return grouped


def _window_click_sum(
    click_dates: np.ndarray,
    click_values: np.ndarray,
    event_days: np.ndarray,
    window: int,
) -> np.ndarray:
    if click_dates.size == 0:
        return np.zeros(len(event_days), dtype=float)

    cumulative = np.cumsum(click_values)
    end_idx = np.searchsorted(click_dates, event_days, side="left") - 1
    start_idx = np.searchsorted(click_dates, event_days - window, side="left") - 1

    totals = np.zeros(len(event_days), dtype=float)
    valid_end = end_idx >= 0
    totals[valid_end] = cumulative[end_idx[valid_end]]

    valid_start = start_idx >= 0
    totals[valid_start] -= cumulative[start_idx[valid_start]]
    return totals


def _attach_click_windows(
    panel: pd.DataFrame,
    daily_clicks: pd.DataFrame,
    windows: Iterable[int],
) -> pd.DataFrame:
    panel = panel.sort_values(["student_course_id", "event_day", "id_assessment"]).copy()
    daily_by_student = {
        key: frame[["date", "sum_click"]].to_numpy()
        for key, frame in daily_clicks.groupby("student_course_id")
    }

    for window in windows:
        panel[f"clicks_{window}d"] = 0.0

    panel["cumulative_clicks"] = 0.0

    pieces: list[pd.DataFrame] = []
    for student_course_id, frame in panel.groupby("student_course_id", sort=False):
        click_array = daily_by_student.get(student_course_id)
        if click_array is None:
            pieces.append(frame)
            continue

        click_dates = click_array[:, 0].astype(float)
        click_values = click_array[:, 1].astype(float)
        event_days = frame["event_day"].to_numpy(dtype=float)

        updated = frame.copy()
        for window in windows:
            updated[f"clicks_{window}d"] = _window_click_sum(
                click_dates=click_dates,
                click_values=click_values,
                event_days=event_days,
                window=window,
            )

        updated["cumulative_clicks"] = _window_click_sum(
            click_dates=click_dates,
            click_values=click_values,
            event_days=event_days,
            window=10_000,
        )
        pieces.append(updated)

    return pd.concat(pieces, ignore_index=True)


def _prepare_base_panel(tables: OULADTables) -> pd.DataFrame:
    assessments = tables.assessments.copy()
    courses = tables.courses.copy()
    student_assessment = tables.student_assessment.copy()
    student_info = tables.student_info.copy()
    student_registration = tables.student_registration.copy()

    assessments["date"] = pd.to_numeric(assessments["date"], errors="coerce")
    courses["module_presentation_length"] = pd.to_numeric(
        courses["module_presentation_length"],
        errors="coerce",
    )
    student_assessment["date_submitted"] = pd.to_numeric(
        student_assessment["date_submitted"],
        errors="coerce",
    )
    student_assessment["score"] = pd.to_numeric(
        student_assessment["score"],
        errors="coerce",
    )

    student_registration["date_registration"] = pd.to_numeric(
        student_registration["date_registration"],
        errors="coerce",
    )
    student_registration["date_unregistration"] = pd.to_numeric(
        student_registration["date_unregistration"],
        errors="coerce",
    )
    student_registration["student_course_id"] = _build_student_course_id(student_registration)

    info_cols = [
        "id_student",
        "code_module",
        "code_presentation",
        "gender",
        "region",
        "highest_education",
        "imd_band",
        "age_band",
        "num_of_prev_attempts",
        "studied_credits",
        "disability",
        "final_result",
    ]
    student_info = student_info[info_cols].copy()
    student_info["student_course_id"] = _build_student_course_id(student_info)

    panel = student_assessment.merge(
        assessments,
        on="id_assessment",
        how="left",
        validate="many_to_one",
        suffixes=("", "_assessment"),
    )
    panel = panel.merge(
        student_info,
        on=["id_student", "code_module", "code_presentation"],
        how="inner",
        validate="many_to_one",
    )
    panel = panel.merge(
        courses,
        on=["code_module", "code_presentation"],
        how="left",
        validate="many_to_one",
    )
    panel = panel.merge(
        student_registration[
            [
                "id_student",
                "code_module",
                "code_presentation",
                "date_registration",
                "date_unregistration",
            ]
        ],
        on=["id_student", "code_module", "code_presentation"],
        how="left",
        validate="many_to_one",
    )

    panel["event_day"] = _coalesce_event_day(panel)
    panel = panel.loc[panel["event_day"].notna()].copy()
    panel["event_day"] = panel["event_day"].astype(float)
    panel["student_course_assessment_id"] = (
        panel["student_course_id"] + "::" + panel["id_assessment"].astype(str)
    )
    panel = panel.sort_values(["student_course_id", "event_day", "id_assessment"])
    panel["assessment_sequence"] = (
        panel.groupby("student_course_id").cumcount() + 1
    )
    panel["assessment_group"] = panel["id_assessment"].astype(str)
    return panel


def build_student_assessment_panel(
    tables: OULADTables,
    config: AnalysisConfig,
) -> pd.DataFrame:
    panel = _prepare_base_panel(tables)
    daily_clicks = _aggregate_daily_clicks(tables.student_vle)
    panel = _attach_click_windows(
        panel=panel,
        daily_clicks=daily_clicks,
        windows=config.lookback_windows,
    )
    panel = add_analysis_variables(panel, config)
    panel = panel.loc[
        panel.groupby("student_course_id")["id_assessment"].transform("size")
        >= config.min_assessments_per_student
    ].copy()
    panel = panel.loc[
        panel["score"].between(config.min_score, config.max_score, inclusive="both")
    ].copy()
    return panel.sort_values(
        ["student_course_id", "event_day", "id_assessment"]
    ).reset_index(drop=True)

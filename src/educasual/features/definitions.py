from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from educasual.config import AnalysisConfig


@dataclass(frozen=True)
class VariableDefinition:
    name: str
    role: str
    description: str


VARIABLE_DICTIONARY = [
    VariableDefinition(
        name="score",
        role="outcome",
        description="Assessment score on a 0-100 scale.",
    ),
    VariableDefinition(
        name="log_clicks_28d",
        role="treatment",
        description="Log(1 + clicks in the 28 days before the assessment).",
    ),
    VariableDefinition(
        name="log_clicks_28d_sq",
        role="robustness",
        description="Squared nonlinear version of the main treatment.",
    ),
    VariableDefinition(
        name="assessment_group",
        role="fixed_effect",
        description="Assessment identifier absorbed as a common assessment effect.",
    ),
    VariableDefinition(
        name="student_course_id",
        role="fixed_effect",
        description="Student-by-course enrollment identifier used for entity fixed effects.",
    ),
    VariableDefinition(
        name="is_low_ses",
        role="heterogeneity",
        description="Indicator for lower-socioeconomic-background students based on IMD band.",
    ),
    VariableDefinition(
        name="is_repeat_student",
        role="heterogeneity",
        description="Indicator for students with at least one prior attempt.",
    ),
    VariableDefinition(
        name="is_female",
        role="heterogeneity",
        description="Indicator for female students.",
    ),
]


_IMD_MIDPOINTS = {
    "0-10%": 5.0,
    "10-20": 15.0,
    "10-20%": 15.0,
    "20-30%": 25.0,
    "30-40%": 35.0,
    "40-50%": 45.0,
    "50-60%": 55.0,
    "60-70%": 65.0,
    "70-80%": 75.0,
    "80-90%": 85.0,
    "90-100%": 95.0,
}


def _imd_midpoint(series: pd.Series) -> pd.Series:
    return series.astype(str).map(_IMD_MIDPOINTS)


def add_analysis_variables(
    panel: pd.DataFrame,
    config: AnalysisConfig,
) -> pd.DataFrame:
    df = panel.copy()

    for window in config.lookback_windows:
        df[f"log_clicks_{window}d"] = np.log1p(df[f"clicks_{window}d"])

    primary_log = f"log_clicks_{config.primary_window}d"
    df[f"{primary_log}_sq"] = df[primary_log] ** 2
    df["imd_midpoint"] = _imd_midpoint(df["imd_band"])
    df["is_low_ses"] = (
        df["imd_midpoint"].fillna(100.0) <= config.low_ses_cutoff
    ).astype(int)
    df["is_repeat_student"] = (
        pd.to_numeric(df["num_of_prev_attempts"], errors="coerce")
        .fillna(0)
        .ge(1)
        .astype(int)
    )
    df["has_disability"] = (
        df["disability"].astype(str).str.strip().str.upper().eq("Y").astype(int)
    )
    df["is_female"] = (
        df["gender"].astype(str).str.strip().str.upper().eq("F").astype(int)
    )
    registration_day = pd.to_numeric(df["date_registration"], errors="coerce")
    unregistration_day = pd.to_numeric(df["date_unregistration"], errors="coerce")
    module_length = pd.to_numeric(df["module_presentation_length"], errors="coerce")
    df["days_since_course_start"] = df["event_day"].clip(lower=0)
    df["days_since_registration"] = (df["event_day"] - registration_day).where(
        registration_day.notna()
    )
    df["days_until_unregistration"] = (unregistration_day - df["event_day"]).where(
        unregistration_day.notna()
    )
    df["relative_progress"] = (df["event_day"] / module_length).where(
        module_length.notna() & (module_length > 0)
    )
    df["is_banked"] = pd.to_numeric(df["is_banked"], errors="coerce").fillna(0).astype(int)
    df["late_submission_days"] = (
        pd.to_numeric(df["date_submitted"], errors="coerce") - df["event_day"]
    ).fillna(0.0)
    df["cumulative_log_clicks"] = np.log1p(df["cumulative_clicks"])
    return df

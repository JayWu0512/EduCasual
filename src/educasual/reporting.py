from __future__ import annotations

import pandas as pd


VARIABLE_LABELS = {
    "score": "Assessment score",
    "clicks_14d": "Pre-assessment clicks (previous 14 days)",
    "clicks_28d": "Pre-assessment clicks (previous 28 days)",
    "clicks_56d": "Pre-assessment clicks (previous 56 days)",
    "log_clicks_14d": "Pre-assessment engagement (log(1 + clicks in previous 14 days))",
    "log_clicks_28d": "Pre-assessment engagement (log(1 + clicks in previous 28 days))",
    "log_clicks_56d": "Pre-assessment engagement (log(1 + clicks in previous 56 days))",
    "log_clicks_28d_sq": "Pre-assessment engagement squared ((log(1 + clicks in previous 28 days))^2)",
    "cumulative_clicks": "Cumulative pre-assessment clicks",
    "cumulative_log_clicks": "Cumulative engagement (log(1 + cumulative clicks))",
    "is_low_ses": "Lower socioeconomic background",
    "is_repeat_student": "Repeat student",
    "is_female": "Female",
}


MODEL_LABELS = {
    "main_fe": "Main FE model",
    "nonlinear_fe": "Nonlinear FE model",
    "alt_window_14d": "Robustness: 14-day window",
    "alt_cumulative": "Robustness: cumulative engagement",
    "clean_non_banked": "Robustness: non-banked only",
    "coursework_only": "Robustness: coursework only",
    "heterogeneity_is_low_ses": "Subgroup: lower SES",
    "heterogeneity_is_repeat_student": "Subgroup: repeat student",
    "heterogeneity_is_female": "Subgroup: gender",
}


def pretty_variable_name(variable: str) -> str:
    if variable in VARIABLE_LABELS:
        return VARIABLE_LABELS[variable]

    if "_x_" in variable:
        left, right = variable.split("_x_", 1)
        return f"{pretty_variable_name(left)} x {pretty_variable_name(right)}"

    return variable


def pretty_model_name(model: str) -> str:
    return MODEL_LABELS.get(model, model)


def make_display_summary(summary: pd.DataFrame) -> pd.DataFrame:
    display = summary.copy()
    display["model_code"] = display["model"]
    display["variable_code"] = display["variable"]
    display["model"] = display["model"].map(pretty_model_name)
    display["variable"] = display["variable"].map(pretty_variable_name)
    ordered_cols = [
        "model",
        "model_code",
        "variable",
        "variable_code",
        "coef",
        "std_error",
        "p_value",
        "nobs",
        "rsquared_within",
    ]
    return display[ordered_cols]

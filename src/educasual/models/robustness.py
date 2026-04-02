from __future__ import annotations

import pandas as pd

from educasual.config import AnalysisConfig
from educasual.models.fixed_effects import fit_fixed_effects_model


def run_model_suite(df: pd.DataFrame, config: AnalysisConfig) -> dict[str, object]:
    primary = config.primary_treatment
    nonlinear_term = f"{primary}_sq"
    models: dict[str, object] = {}

    models["main_fe"] = fit_fixed_effects_model(
        df=df,
        outcome=config.outcome,
        regressors=[primary],
        assessment_effect=config.assessment_effect,
    )

    models["nonlinear_fe"] = fit_fixed_effects_model(
        df=df,
        outcome=config.outcome,
        regressors=[primary, nonlinear_term],
        assessment_effect=config.assessment_effect,
    )

    alternative_treatment = "log_clicks_14d"
    if alternative_treatment in df.columns:
        models["alt_window_14d"] = fit_fixed_effects_model(
            df=df,
            outcome=config.outcome,
            regressors=[alternative_treatment],
            assessment_effect=config.assessment_effect,
        )

    cumulative_treatment = "cumulative_log_clicks"
    if cumulative_treatment in df.columns:
        models["alt_cumulative"] = fit_fixed_effects_model(
            df=df,
            outcome=config.outcome,
            regressors=[cumulative_treatment],
            assessment_effect=config.assessment_effect,
        )

    clean_sample = df.loc[df["is_banked"].eq(0)].copy()
    if len(clean_sample) < len(df):
        models["clean_non_banked"] = fit_fixed_effects_model(
            df=clean_sample,
            outcome=config.outcome,
            regressors=[primary],
            assessment_effect=config.assessment_effect,
        )

    coursework_only = df.loc[df["assessment_type"].isin(["TMA", "CMA"])].copy()
    if not coursework_only.empty:
        models["coursework_only"] = fit_fixed_effects_model(
            df=coursework_only,
            outcome=config.outcome,
            regressors=[primary],
            assessment_effect=config.assessment_effect,
        )

    for subgroup in config.heterogeneity_groups:
        interaction_col = f"{primary}_x_{subgroup}"
        if subgroup not in df.columns:
            continue
        enriched = df.copy()
        enriched[interaction_col] = enriched[primary] * enriched[subgroup]
        models[f"heterogeneity_{subgroup}"] = fit_fixed_effects_model(
            df=enriched,
            outcome=config.outcome,
            regressors=[primary, interaction_col],
            assessment_effect=config.assessment_effect,
        )

    return models

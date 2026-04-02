from __future__ import annotations

from collections.abc import Mapping, Sequence

import pandas as pd
from linearmodels.panel import PanelOLS


def prepare_panel_index(
    df: pd.DataFrame,
    entity_col: str = "student_course_id",
    time_col: str = "assessment_sequence",
) -> pd.DataFrame:
    panel = df.copy()
    panel = panel.sort_values([entity_col, time_col, "id_assessment"])
    return panel.set_index([entity_col, time_col])


def fit_fixed_effects_model(
    df: pd.DataFrame,
    outcome: str,
    regressors: Sequence[str],
    assessment_effect: str = "assessment_group",
    cluster_entity: bool = True,
) -> object:
    panel = prepare_panel_index(df)
    exog = panel[list(regressors)].astype(float)
    other_effects = panel[[assessment_effect]].astype(str)

    model = PanelOLS(
        dependent=panel[outcome].astype(float),
        exog=exog,
        entity_effects=True,
        other_effects=other_effects,
        drop_absorbed=True,
        check_rank=False,
    )
    return model.fit(cov_type="clustered", cluster_entity=cluster_entity)


def collect_model_summaries(results: Mapping[str, object]) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for model_name, result in results.items():
        params = result.params
        std_errors = result.std_errors
        pvalues = result.pvalues
        for variable in params.index:
            rows.append(
                {
                    "model": model_name,
                    "variable": variable,
                    "coef": float(params[variable]),
                    "std_error": float(std_errors[variable]),
                    "p_value": float(pvalues[variable]),
                    "nobs": float(result.nobs),
                    "rsquared_within": float(result.rsquared_within),
                }
            )
    return pd.DataFrame(rows)

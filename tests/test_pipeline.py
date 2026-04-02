from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from educasual.config import load_analysis_config
from educasual.data.build_panel import build_student_assessment_panel
from educasual.data.io import OULADTables
from educasual.models.fixed_effects import collect_model_summaries
from educasual.models.robustness import run_model_suite


def _make_synthetic_tables() -> OULADTables:
    assessments = pd.DataFrame(
        {
            "id_assessment": [101, 102, 103],
            "code_module": ["AAA", "AAA", "AAA"],
            "code_presentation": ["2014J", "2014J", "2014J"],
            "assessment_type": ["TMA", "TMA", "Exam"],
            "date": [10, 20, 30],
            "weight": [20.0, 30.0, 50.0],
        }
    )

    student_info = pd.DataFrame(
        {
            "id_student": [1, 2],
            "code_module": ["AAA", "AAA"],
            "code_presentation": ["2014J", "2014J"],
            "gender": ["F", "M"],
            "region": ["East", "West"],
            "highest_education": ["A Level", "HE Qualification"],
            "imd_band": ["20-30%", "60-70%"],
            "age_band": ["0-35", "0-35"],
            "num_of_prev_attempts": [0, 1],
            "studied_credits": [60, 60],
            "disability": ["N", "N"],
            "final_result": ["Pass", "Pass"],
        }
    )

    student_assessment = pd.DataFrame(
        {
            "id_assessment": [101, 102, 103, 101, 102, 103],
            "id_student": [1, 1, 1, 2, 2, 2],
            "date_submitted": [10, 20, 30, 10, 20, 30],
            "is_banked": [0, 0, 0, 0, 0, 0],
            "score": [60, 70, 81, 55, 63, 71],
        }
    )

    student_vle = pd.DataFrame(
        {
            "code_module": ["AAA"] * 12,
            "code_presentation": ["2014J"] * 12,
            "id_student": [1] * 6 + [2] * 6,
            "id_site": [1] * 12,
            "date": [2, 6, 9, 15, 19, 27, 2, 7, 9, 15, 19, 27],
            "sum_click": [5, 6, 7, 8, 9, 10, 3, 4, 5, 6, 7, 8],
        }
    )

    vle = pd.DataFrame(
        {
            "id_site": [1],
            "code_module": ["AAA"],
            "code_presentation": ["2014J"],
            "activity_type": ["content"],
            "week_from": [0],
            "week_to": [30],
        }
    )

    return OULADTables(
        assessments=assessments,
        courses=pd.DataFrame(
            {
                "code_module": ["AAA"],
                "code_presentation": ["2014J"],
                "module_presentation_length": [30],
            }
        ),
        student_assessment=student_assessment,
        student_info=student_info,
        student_registration=pd.DataFrame(
            {
                "code_module": ["AAA", "AAA"],
                "code_presentation": ["2014J", "2014J"],
                "id_student": [1, 2],
                "date_registration": [-5, -4],
                "date_unregistration": [None, None],
            }
        ),
        student_vle=student_vle,
        vle=vle,
    )


def test_build_student_assessment_panel_creates_expected_columns() -> None:
    config = load_analysis_config()
    tables = _make_synthetic_tables()

    panel = build_student_assessment_panel(tables, config)

    assert len(panel) == 6
    assert {"clicks_14d", "clicks_28d", "log_clicks_28d", "is_low_ses"} <= set(panel.columns)

    row = panel.loc[
        (panel["id_student"] == 1) & (panel["id_assessment"] == 101)
    ].iloc[0]
    assert math.isclose(row["clicks_14d"], 18.0)
    assert math.isclose(row["clicks_28d"], 18.0)
    assert math.isclose(row["log_clicks_28d"], math.log1p(18.0))
    assert row["is_low_ses"] == 1


def test_run_model_suite_returns_nonempty_summary() -> None:
    config = load_analysis_config()
    tables = _make_synthetic_tables()
    panel = build_student_assessment_panel(tables, config)

    results = run_model_suite(panel, config)
    summary = collect_model_summaries(results)

    assert "main_fe" in results
    assert not summary.empty
    assert (summary["model"] == "main_fe").any()
    assert (summary["variable"] == config.primary_treatment).any()

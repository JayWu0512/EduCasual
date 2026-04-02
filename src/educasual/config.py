from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProjectPaths:
    root: Path = PROJECT_ROOT
    raw_data: Path = PROJECT_ROOT / "data" / "raw" / "oulad"
    processed_data: Path = PROJECT_ROOT / "data" / "processed"
    results: Path = PROJECT_ROOT / "results"
    figures: Path = PROJECT_ROOT / "results" / "figures"
    tables: Path = PROJECT_ROOT / "results" / "tables"
    docs: Path = PROJECT_ROOT / "docs"
    config: Path = PROJECT_ROOT / "config"


@dataclass(frozen=True)
class AnalysisConfig:
    lookback_windows: tuple[int, ...]
    primary_window: int
    min_assessments_per_student: int
    min_score: float
    max_score: float
    low_ses_cutoff: float
    primary_treatment: str
    outcome: str
    assessment_effect: str
    heterogeneity_groups: tuple[str, ...]


def load_analysis_config(config_path: Path | None = None) -> AnalysisConfig:
    path = config_path or (PROJECT_ROOT / "config" / "analysis.yaml")
    with path.open("r", encoding="utf-8") as handle:
        raw: dict[str, Any] = yaml.safe_load(handle)

    return AnalysisConfig(
        lookback_windows=tuple(raw["lookback_windows"]),
        primary_window=int(raw["primary_window"]),
        min_assessments_per_student=int(raw["min_assessments_per_student"]),
        min_score=float(raw["min_score"]),
        max_score=float(raw["max_score"]),
        low_ses_cutoff=float(raw["low_ses_cutoff"]),
        primary_treatment=str(raw["primary_treatment"]),
        outcome=str(raw["outcome"]),
        assessment_effect=str(raw["assessment_effect"]),
        heterogeneity_groups=tuple(raw["heterogeneity_groups"]),
    )

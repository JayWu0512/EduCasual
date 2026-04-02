"""EduCasual research package for the OULAD final project."""

from .config import AnalysisConfig, ProjectPaths, load_analysis_config
from .reporting import pretty_model_name, pretty_variable_name

__all__ = [
    "AnalysisConfig",
    "ProjectPaths",
    "load_analysis_config",
    "pretty_model_name",
    "pretty_variable_name",
]

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from educasual.config import ProjectPaths, load_analysis_config
from educasual.data import build_student_assessment_panel, load_oulad_tables
from educasual.models import collect_model_summaries, run_model_suite
from educasual.reporting import make_display_summary


def build_panel_dataset(raw_dir: Path, output_path: Path | None = None) -> pd.DataFrame:
    config = load_analysis_config()
    tables = load_oulad_tables(raw_dir)
    panel = build_student_assessment_panel(tables, config)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        panel.to_csv(output_path, index=False)
    return panel


def run_analysis(panel: pd.DataFrame, project_paths: ProjectPaths) -> dict[str, object]:
    config = load_analysis_config()
    from educasual.visualization import (
        plot_click_distribution,
        plot_decile_relationship,
        plot_heterogeneity_relationship,
    )

    results = run_model_suite(panel, config)
    summary = collect_model_summaries(results)
    display_summary = make_display_summary(summary)

    project_paths.tables.mkdir(parents=True, exist_ok=True)
    display_summary.to_csv(project_paths.tables / "model_summary.csv", index=False)

    plot_click_distribution(
        panel,
        treatment=config.primary_treatment,
        output_path=project_paths.figures / "01_click_distribution.png",
    )
    plot_decile_relationship(
        panel,
        treatment=config.primary_treatment,
        outcome=config.outcome,
        output_path=project_paths.figures / "02_main_relationship.png",
    )
    plot_heterogeneity_relationship(
        panel,
        treatment=config.primary_treatment,
        outcome=config.outcome,
        subgroup="is_low_ses",
        output_path=project_paths.figures / "03_low_ses_heterogeneity.png",
    )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="EduCasual OULAD analysis pipeline")
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=ProjectPaths().raw_data,
        help="Directory containing OULAD CSV files.",
    )
    parser.add_argument(
        "--panel-out",
        type=Path,
        default=ProjectPaths().processed_data / "student_assessment_panel.csv",
        help="Output path for the clean panel dataset.",
    )
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Only build the clean panel without estimating models or figures.",
    )
    args = parser.parse_args()

    paths = ProjectPaths()
    panel = build_panel_dataset(raw_dir=args.raw_dir, output_path=args.panel_out)

    if not args.skip_analysis:
        run_analysis(panel=panel, project_paths=paths)


if __name__ == "__main__":
    main()

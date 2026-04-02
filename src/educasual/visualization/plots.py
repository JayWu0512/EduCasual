from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from educasual.reporting import pretty_variable_name


sns.set_theme(style="whitegrid", context="talk")


def _save_or_show(fig: plt.Figure, output_path: Path | None) -> plt.Figure:
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=200)
    return fig


def plot_click_distribution(
    panel: pd.DataFrame,
    treatment: str = "log_clicks_28d",
    output_path: Path | None = None,
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(panel[treatment], bins=30, kde=True, color="#2f5d62", ax=ax)
    ax.set_title("Distribution of Pre-Assessment Engagement")
    ax.set_xlabel(pretty_variable_name(treatment))
    ax.set_ylabel("Number of observations")
    return _save_or_show(fig, output_path)


def plot_decile_relationship(
    panel: pd.DataFrame,
    treatment: str = "log_clicks_28d",
    outcome: str = "score",
    output_path: Path | None = None,
) -> plt.Figure:
    plot_df = panel[[treatment, outcome]].dropna().copy()
    plot_df["engagement_decile"] = pd.qcut(
        plot_df[treatment],
        q=10,
        duplicates="drop",
    )
    summary = (
        plot_df.groupby("engagement_decile", observed=False)
        .agg(mean_treatment=(treatment, "mean"), mean_score=(outcome, "mean"))
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(
        data=summary,
        x="mean_treatment",
        y="mean_score",
        marker="o",
        linewidth=2.5,
        color="#0b6e4f",
        ax=ax,
    )
    ax.set_title("Average Score by Engagement Decile")
    ax.set_xlabel(pretty_variable_name(treatment))
    ax.set_ylabel("Average assessment score")
    return _save_or_show(fig, output_path)


def plot_heterogeneity_relationship(
    panel: pd.DataFrame,
    treatment: str = "log_clicks_28d",
    outcome: str = "score",
    subgroup: str = "is_low_ses",
    subgroup_labels: tuple[str, str] = ("Higher SES", "Lower SES"),
    output_path: Path | None = None,
) -> plt.Figure:
    plot_df = panel[[treatment, outcome, subgroup]].dropna().copy()
    plot_df["group_label"] = plot_df[subgroup].map(
        {0: subgroup_labels[0], 1: subgroup_labels[1]}
    )
    plot_df["engagement_bin"] = pd.qcut(
        plot_df[treatment],
        q=8,
        duplicates="drop",
    )
    summary = (
        plot_df.groupby(["group_label", "engagement_bin"], observed=False)
        .agg(mean_treatment=(treatment, "mean"), mean_score=(outcome, "mean"))
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(
        data=summary,
        x="mean_treatment",
        y="mean_score",
        hue="group_label",
        marker="o",
        linewidth=2.5,
        palette=["#415a77", "#d97706"],
        ax=ax,
    )
    ax.set_title("Engagement-Performance Relationship by Subgroup")
    ax.set_xlabel(pretty_variable_name(treatment))
    ax.set_ylabel("Average assessment score")
    ax.legend(title="")
    return _save_or_show(fig, output_path)

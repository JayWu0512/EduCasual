# EduCasual

This repository implements the IDS 701 final project proposed in `IDS 701 Final Project Proposal.pdf`:

`Does an increase in online engagement prior to an assessment cause an increase in student performance on that assessment?`

The project is organized around a clean `student-assessment` panel built from the Open University Learning Analytics Dataset (OULAD), a main student fixed-effects model, several robustness checks, subgroup analyses, and notebook-based result presentation.

## Research Design

### Clear Question

We study whether students perform better on a given assessment when they are more engaged than usual before that assessment.

- Treatment: pre-assessment online engagement, measured mainly as `log(1 + clicks_28d)`.
- Treatment: pre-assessment engagement, displayed as `Pre-assessment engagement (log(1 + clicks in previous 28 days))`.
- Outcome: assessment `score` on a 0-100 scale.
- Unit of observation: `student-course-assessment`.
- Identification logic: compare the same student-course enrollment to itself over time using entity fixed effects and common assessment effects.

### Main Identification Strategy

The baseline estimating equation is:

```text
score_{i,a} = beta * Pre-assessment engagement (log(1 + clicks in previous 28 days))_{i,a} + alpha_i + delta_a + epsilon_{i,a}
```

- `alpha_i`: student-course fixed effects.
- `delta_a`: assessment fixed effects.
- Engagement is measured only before the assessment date, which helps reduce reverse-timing concerns.

### Robustness And Heterogeneity

The pipeline includes:

1. A nonlinear fixed-effects model with `Pre-assessment engagement squared ((log(1 + clicks in previous 28 days))^2)` to test nonlinear patterns.
2. Alternative treatment definitions using a shorter window (`14d`) and cumulative clicks.
3. Cleaner-sample robustness checks that exclude banked scores and isolate coursework assessments.
4. Heterogeneity analyses for:
   - lower socioeconomic background (`is_low_ses`)
   - repeat students (`is_repeat_student`)
   - gender (`is_female`)

## Project Structure

```text
EduCasual/
├── config/
│   └── analysis.yaml
├── data/
│   ├── raw/oulad/
│   └── processed/
├── docs/
│   └── variable_dictionary.md
├── notebooks/
│   └── 01_main_analysis.ipynb
├── results/
│   ├── figures/
│   └── tables/
├── src/educasual/
│   ├── config.py
│   ├── pipeline.py
│   ├── data/
│   ├── features/
│   ├── models/
│   └── visualization/
├── tests/
│   └── test_pipeline.py
└── requirements.txt
```

## Data Requirements

Place the following OULAD files inside [`data/raw/oulad`](/Users/sungtsewu/Desktop/temp_github/EduCasual/data/raw/oulad):

- `assessments.csv`
- `courses.csv`
- `studentAssessment.csv`
- `studentInfo.csv`
- `studentRegistration.csv`
- `studentVle.csv`
- `vle.csv`

The expected source in the proposal is the UCI Machine Learning Repository OULAD release.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Build The Clean Panel

```bash
PYTHONPATH=src python -m educasual.pipeline --skip-analysis
```

This writes:

- [`data/processed/student_assessment_panel.csv`](/Users/sungtsewu/Desktop/temp_github/EduCasual/data/processed/student_assessment_panel.csv)

## Run The Full Analysis

```bash
PYTHONPATH=src python -m educasual.pipeline
```

This produces:

- a clean panel dataset
- a sample summary table at [`results/tables/panel_summary.csv`](/Users/sungtsewu/Desktop/temp_github/EduCasual/results/tables/panel_summary.csv)
- model summary table at [`results/tables/model_summary.csv`](/Users/sungtsewu/Desktop/temp_github/EduCasual/results/tables/model_summary.csv)
- figures in [`results/figures`](/Users/sungtsewu/Desktop/temp_github/EduCasual/results/figures)
- a written result summary at [`docs/analysis_summary.md`](/Users/sungtsewu/Desktop/temp_github/EduCasual/docs/analysis_summary.md)

## Notebook Workflow

Use [`notebooks/01_main_analysis.ipynb`](/Users/sungtsewu/Desktop/temp_github/EduCasual/notebooks/01_main_analysis.ipynb) for the final narrative deliverable. The notebook calls the reusable functions in `src/` instead of duplicating logic.

Suggested presentation order:

1. One clear causal question.
2. One clean panel dataset.
3. One main fixed-effects model.
4. Two to three robustness and subgroup analyses.
5. A small set of clean figures.

## Key Source Modules

- [`src/educasual/data/build_panel.py`](/Users/sungtsewu/Desktop/temp_github/EduCasual/src/educasual/data/build_panel.py): panel construction and pre-assessment click windows.
- [`src/educasual/features/definitions.py`](/Users/sungtsewu/Desktop/temp_github/EduCasual/src/educasual/features/definitions.py): variable definitions and engineered analysis columns.
- [`src/educasual/models/fixed_effects.py`](/Users/sungtsewu/Desktop/temp_github/EduCasual/src/educasual/models/fixed_effects.py): fixed-effects estimation wrapper.
- [`src/educasual/models/robustness.py`](/Users/sungtsewu/Desktop/temp_github/EduCasual/src/educasual/models/robustness.py): baseline, robustness, and heterogeneity model suite.
- [`src/educasual/visualization/plots.py`](/Users/sungtsewu/Desktop/temp_github/EduCasual/src/educasual/visualization/plots.py): notebook-ready figure functions.

## Notes

- Time-invariant controls are documented and preserved in the panel, but the main student fixed-effects estimator does not separately identify their level effects.
- The subgroup models identify differential engagement slopes via interaction terms.
- If the raw OULAD data is not present, the codebase structure, tests, notebook, and documentation still remain ready for execution once the files are added.

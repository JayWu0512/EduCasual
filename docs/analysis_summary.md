# Analysis Summary

## Question

Does higher online engagement before an assessment improve that same student's assessment performance?

## Final Analytic Sample

Using OULAD, the cleaned panel contains:

- 171,241 student-assessment observations
- 21,342 unique students
- 23,322 student-course panels
- 188 unique assessments

The main treatment is `Pre-assessment engagement (log(1 + clicks in previous 28 days))`. The main outcome is assessment `score`.

## Main Fixed-Effects Result

Baseline model:

```text
score_ia = beta * Pre-assessment engagement (log(1 + clicks in previous 28 days))_ia + student-course FE + assessment FE + error_ia
```

Main estimate:

- `beta = 1.219` with clustered SE `0.053`
- `p < 0.001`

Interpretation:

- Within the same student-course enrollment, higher pre-assessment engagement is associated with higher assessment scores.
- The effect is modest but precisely estimated.

## Robustness Checks

The main result is directionally stable across alternative specifications:

- `14-day window`: coefficient `0.922`, `p < 0.001`
- `non-banked sample only`: coefficient `1.267`, `p < 0.001`
- `coursework only (TMA/CMA)`: coefficient `1.178`, `p < 0.001`
- `cumulative engagement`: coefficient `2.696`, `p < 0.001`

The nonlinear specification does not support the original diminishing-returns hypothesis in a simple quadratic FE model:

- linear term `-0.229`, `p = 0.113`
- quadratic term `0.202`, `p < 0.001`

This means the current quadratic FE model does not produce a clean concave pattern.

## Heterogeneity

The interaction results are small and not statistically precise:

- low SES interaction: `-0.035`, `p = 0.718`
- repeat student interaction: `-0.022`, `p = 0.877`
- female interaction: `-0.074`, `p = 0.455`

Interpretation:

- The positive engagement-performance relationship appears broadly similar across these observed subgroups in the current design.
- The main evidence is stronger for the average within-student effect than for subgroup differences.

## Deliverables Produced

- Clean panel: [`data/processed/student_assessment_panel.csv`](/Users/sungtsewu/Desktop/temp_github/EduCasual/data/processed/student_assessment_panel.csv)
- Sample summary: [`results/tables/panel_summary.csv`](/Users/sungtsewu/Desktop/temp_github/EduCasual/results/tables/panel_summary.csv)
- Model summary: [`results/tables/model_summary.csv`](/Users/sungtsewu/Desktop/temp_github/EduCasual/results/tables/model_summary.csv)
- Figures:
  - [`01_click_distribution.png`](/Users/sungtsewu/Desktop/temp_github/EduCasual/results/figures/01_click_distribution.png)
  - [`02_main_relationship.png`](/Users/sungtsewu/Desktop/temp_github/EduCasual/results/figures/02_main_relationship.png)
  - [`03_low_ses_heterogeneity.png`](/Users/sungtsewu/Desktop/temp_github/EduCasual/results/figures/03_low_ses_heterogeneity.png)
  - [`04_gender_heterogeneity.png`](/Users/sungtsewu/Desktop/temp_github/EduCasual/results/figures/04_gender_heterogeneity.png)

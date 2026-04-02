# Variable Dictionary

This project uses an assessment-level panel built from OULAD. The core analysis variables are defined in [`src/educasual/features/definitions.py`](/Users/sungtsewu/Desktop/temp_github/EduCasual/src/educasual/features/definitions.py).

## Identifiers

| Variable | Description |
| --- | --- |
| `id_student` | Original OULAD student identifier. |
| `id_assessment` | Original OULAD assessment identifier. |
| `student_course_id` | Composite entity id: `id_student::code_module::code_presentation`. |
| `student_course_assessment_id` | Composite row id for one student-course-assessment record. |
| `assessment_group` | Assessment effect absorbed in the FE models. |

## Timing

| Variable | Description |
| --- | --- |
| `date` | Planned assessment date from `assessments.csv`. |
| `date_submitted` | Submission day from `studentAssessment.csv`. |
| `event_day` | Main event timing used for the panel. Uses `date`, and falls back to `date_submitted` if needed. |
| `assessment_sequence` | Order of assessments within a student-course panel. |

## Outcome

| Variable | Description |
| --- | --- |
| `score` | Assessment score on a 0-100 scale. |

## Main Treatment

| Variable | Description |
| --- | --- |
| `clicks_14d` | Clicks in the 14 days before `event_day`. |
| `clicks_28d` | Clicks in the 28 days before `event_day`. Main raw treatment. |
| `clicks_56d` | Clicks in the 56 days before `event_day`. |
| `log_clicks_14d` | `Pre-assessment engagement (log(1 + clicks in previous 14 days))`. |
| `log_clicks_28d` | `Pre-assessment engagement (log(1 + clicks in previous 28 days))`. Main treatment used in the baseline FE model. |
| `log_clicks_56d` | `Pre-assessment engagement (log(1 + clicks in previous 56 days))`. |
| `cumulative_clicks` | Cumulative clicks prior to the assessment. |
| `cumulative_log_clicks` | `Cumulative engagement (log(1 + cumulative clicks))`. |
| `log_clicks_28d_sq` | `Pre-assessment engagement squared ((log(1 + clicks in previous 28 days))^2)`. |

## Background And Heterogeneity Variables

| Variable | Description |
| --- | --- |
| `gender` | Student gender from OULAD. |
| `imd_band` | Socioeconomic deprivation band from OULAD. |
| `imd_midpoint` | Numeric midpoint mapped from `imd_band`. |
| `is_low_ses` | Indicator for `imd_midpoint <= 40`. |
| `num_of_prev_attempts` | Number of previous attempts in OULAD. |
| `is_repeat_student` | Indicator for at least one previous attempt. |
| `is_female` | Indicator for female students. |
| `disability` | OULAD disability indicator. |
| `has_disability` | Binary disability indicator. |
| `date_registration` | Registration day from OULAD. |
| `date_unregistration` | Unregistration day from OULAD. |
| `module_presentation_length` | Course length from `courses.csv`. |

## Additional Descriptive Variables

| Variable | Description |
| --- | --- |
| `days_since_course_start` | `event_day` clipped at zero for descriptive use. |
| `days_since_registration` | Assessment day relative to student registration. |
| `days_until_unregistration` | Remaining days until unregistration, if observed. |
| `relative_progress` | `event_day / module_presentation_length`. |
| `late_submission_days` | `date_submitted - event_day`, with missing values filled by zero. |
| `studied_credits` | Enrolled credits from OULAD. |
| `highest_education` | Highest education group from OULAD. |
| `region` | Student region from OULAD. |
| `final_result` | Final course result from OULAD. |

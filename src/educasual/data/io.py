from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


REQUIRED_OULAD_FILES = {
    "assessments": "assessments.csv",
    "courses": "courses.csv",
    "student_assessment": "studentAssessment.csv",
    "student_info": "studentInfo.csv",
    "student_registration": "studentRegistration.csv",
    "student_vle": "studentVle.csv",
    "vle": "vle.csv",
}


@dataclass(frozen=True)
class OULADTables:
    assessments: pd.DataFrame
    courses: pd.DataFrame
    student_assessment: pd.DataFrame
    student_info: pd.DataFrame
    student_registration: pd.DataFrame
    student_vle: pd.DataFrame
    vle: pd.DataFrame


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, na_values=["?"])


def load_oulad_tables(raw_dir: Path) -> OULADTables:
    missing = [
        filename
        for filename in REQUIRED_OULAD_FILES.values()
        if not (raw_dir / filename).exists()
    ]
    if missing:
        raise FileNotFoundError(
            "Missing required OULAD files in "
            f"{raw_dir}: {', '.join(sorted(missing))}"
        )

    return OULADTables(
        assessments=_read_csv(raw_dir / REQUIRED_OULAD_FILES["assessments"]),
        courses=_read_csv(raw_dir / REQUIRED_OULAD_FILES["courses"]),
        student_assessment=_read_csv(raw_dir / REQUIRED_OULAD_FILES["student_assessment"]),
        student_info=_read_csv(raw_dir / REQUIRED_OULAD_FILES["student_info"]),
        student_registration=_read_csv(raw_dir / REQUIRED_OULAD_FILES["student_registration"]),
        student_vle=_read_csv(raw_dir / REQUIRED_OULAD_FILES["student_vle"]),
        vle=_read_csv(raw_dir / REQUIRED_OULAD_FILES["vle"]),
    )

from __future__ import annotations

from typing import Dict, Any
import pandas as pd


REQUIRED_COLS = [
    "date",
    "user_id",
    "age_group",
    "primary_device",
    "internet_type",
    "social_media_hours",
    "work_or_study_hours",
    "entertainment_hours",
    "total_screen_time",
]


def validate_schema(df: pd.DataFrame) -> Dict[str, Any]:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    return {
        "n_rows": int(len(df)),
        "n_cols": int(df.shape[1]),
        "missing_required_cols": missing,
        "has_missing_values": bool(df.isna().any().any()),
        "duplicate_user_id": int(df["user_id"].duplicated().sum()) if "user_id" in df.columns else None,
    }


def validate_identity(df: pd.DataFrame) -> Dict[str, Any]:
    if not set(["total_screen_time", "social_media_hours", "work_or_study_hours", "entertainment_hours"]).issubset(df.columns):
        return {"identity_check_run": False}

    lhs = pd.to_numeric(df["total_screen_time"], errors="coerce")
    rhs = (
        pd.to_numeric(df["social_media_hours"], errors="coerce")
        + pd.to_numeric(df["work_or_study_hours"], errors="coerce")
        + pd.to_numeric(df["entertainment_hours"], errors="coerce")
    )
    diff = (lhs - rhs).abs()
    return {
        "identity_check_run": True,
        "max_abs_diff": float(diff.max()),
        "rows_failing": int((diff > 1e-9).sum()),
    }

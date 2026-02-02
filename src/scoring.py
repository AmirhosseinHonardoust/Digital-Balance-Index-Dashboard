from __future__ import annotations

import numpy as np
import pandas as pd


def _safe_div(num: pd.Series, den: pd.Series) -> pd.Series:
    den = den.replace(0, np.nan)
    return num / den


def compute_shares(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    total = pd.to_numeric(out["total_screen_time"], errors="coerce")
    out["p_social"] = _safe_div(pd.to_numeric(out["social_media_hours"], errors="coerce"), total)
    out["p_work"] = _safe_div(pd.to_numeric(out["work_or_study_hours"], errors="coerce"), total)
    out["p_entertainment"] = _safe_div(pd.to_numeric(out["entertainment_hours"], errors="coerce"), total)
    return out


def compute_dbi(df: pd.DataFrame) -> pd.DataFrame:
    """
    DBI = normalized Shannon entropy over (p_social, p_work, p_entertainment).
    Range: [0, 1]
    """
    out = df.copy()
    p = out[["p_social", "p_work", "p_entertainment"]].astype(float)

    # treat 0*log(0)=0 by excluding zeros from log term
    p_safe = p.replace(0.0, np.nan)
    entropy = -(p * np.log(p_safe)).sum(axis=1, skipna=True)  # natural log
    out["entropy"] = entropy
    out["dbi"] = entropy / np.log(3)
    return out


def compute_dominance(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    pcols = ["p_social", "p_work", "p_entertainment"]
    out["dominance"] = out[pcols].max(axis=1)
    out["dominant_category"] = out[pcols].idxmax(axis=1).map({
        "p_social": "Social",
        "p_work": "Work/Study",
        "p_entertainment": "Entertainment",
    })
    return out


def add_tiers(df: pd.DataFrame, dbi_balanced: float = 0.80, dbi_mixed: float = 0.60):
    out = df.copy()

    def dbi_tier(x):
        if pd.isna(x):
            return "Unknown"
        if x >= dbi_balanced:
            return "Balanced"
        if x >= dbi_mixed:
            return "Mixed"
        return "Skewed"

    out["dbi_tier"] = out["dbi"].apply(dbi_tier)

    total = pd.to_numeric(out["total_screen_time"], errors="coerce")
    q33 = float(total.quantile(0.33))
    q66 = float(total.quantile(0.66))

    def load_tier(x):
        if pd.isna(x):
            return "Unknown"
        if x < q33:
            return "Low"
        if x < q66:
            return "Medium"
        return "High"

    out["load_tier"] = total.apply(load_tier)
    out["flag_highload_skewed"] = (out["load_tier"].eq("High") & out["dbi_tier"].eq("Skewed")).astype(int)

    meta = {
        "dbi_thresholds": {"balanced_ge": dbi_balanced, "mixed_ge": dbi_mixed},
        "load_quantiles": {"q33": q33, "q66": q66},
    }
    return out, meta

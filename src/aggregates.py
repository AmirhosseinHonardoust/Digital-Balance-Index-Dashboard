from __future__ import annotations

import pandas as pd


def segment_summary(df: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["age_group", "primary_device", "internet_type"]
    agg = df.groupby(group_cols, dropna=False).agg(
        n=("user_id", "size"),
        total_mean=("total_screen_time", "mean"),
        total_median=("total_screen_time", "median"),
        dbi_mean=("dbi", "mean"),
        dbi_median=("dbi", "median"),
        dominance_mean=("dominance", "mean"),
        highload_skewed_rate=("flag_highload_skewed", "mean"),
        social_share_mean=("p_social", "mean"),
        work_share_mean=("p_work", "mean"),
        entertainment_share_mean=("p_entertainment", "mean"),
    ).reset_index()

    agg["highload_skewed_rate"] = agg["highload_skewed_rate"] * 100.0
    return agg.sort_values(["highload_skewed_rate", "dbi_mean"], ascending=[False, True])


def daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"], errors="coerce")
    g = d.groupby("date", dropna=False).agg(
        n=("user_id", "size"),
        total_mean=("total_screen_time", "mean"),
        dbi_mean=("dbi", "mean"),
        balanced_rate=("dbi_tier", lambda s: (s == "Balanced").mean() * 100.0),
        skewed_rate=("dbi_tier", lambda s: (s == "Skewed").mean() * 100.0),
    ).reset_index().sort_values("date")
    return g

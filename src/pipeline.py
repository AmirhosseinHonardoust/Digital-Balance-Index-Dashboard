from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import matplotlib.pyplot as plt

from src.io import read_csv, write_csv, write_json
from src.validate import validate_schema, validate_identity
from src.scoring import compute_shares, compute_dbi, compute_dominance, add_tiers
from src.aggregates import segment_summary, daily_summary
from src.reporting import save_hist, save_scatter, save_bar, save_heatmap


def run(
    input_path: str,
    out_dir: str = "outputs",
    figures_dir: str = "reports/figures",
) -> Dict[str, Any]:
    out_dir = Path(out_dir)
    fig_dir = Path(figures_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = read_csv(input_path)

    # Parse types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    schema = validate_schema(df)
    identity = validate_identity(df)

    if schema["missing_required_cols"]:
        raise ValueError(f"Missing required columns: {schema['missing_required_cols']}")

    # Score
    scored = compute_shares(df)
    scored = compute_dbi(scored)
    scored = compute_dominance(scored)
    scored, tier_meta = add_tiers(scored)

    # Save processed copy (nice to keep)
    proc_path = Path("data/processed/scored_rows.csv")
    proc_path.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(proc_path, index=False)

    # Aggregates
    seg = segment_summary(scored)
    daily = daily_summary(scored)

    # Export outputs
    write_csv(scored, out_dir / "scored_rows.csv")
    write_csv(seg, out_dir / "segment_summary.csv")
    write_csv(daily, out_dir / "daily_summary.csv")

    # Metric cards
    kpi = {
        "n_rows": int(len(scored)),
        "n_days": int(daily["date"].nunique()),
        "avg_total_screen_time": float(pd.to_numeric(scored["total_screen_time"], errors="coerce").mean()),
        "avg_dbi": float(scored["dbi"].mean()),
        "balanced_rate_pct": float((scored["dbi_tier"] == "Balanced").mean() * 100.0),
        "skewed_rate_pct": float((scored["dbi_tier"] == "Skewed").mean() * 100.0),
        "highload_skewed_rate_pct": float(scored["flag_highload_skewed"].mean() * 100.0),
        "thresholds": tier_meta,
        "validation": {"schema": schema, "identity": identity},
    }
    write_json(kpi, out_dir / "metric_cards.json")

    # Figures
    save_hist(scored["dbi"], "DBI distribution", fig_dir / "dbi_distribution.png", bins=30, xlabel="DBI (0–1)")
    save_scatter(
        pd.to_numeric(scored["total_screen_time"], errors="coerce"),
        scored["dbi"],
        "Total screen time vs DBI",
        fig_dir / "total_vs_dbi_scatter.png",
        xlabel="Total screen time (hours)",
        ylabel="DBI (0–1)",
    )

    # Composition by age group (mean shares)
    comp_age = scored.groupby("age_group", dropna=False)[["p_social", "p_work", "p_entertainment"]].mean().sort_index()
    comp_age.columns = ["Social", "Work/Study", "Entertainment"]
    comp_age.plot(kind="bar", stacked=True, title="Composition by age group (mean shares)")
    plt.ylabel("Share of total screen time")
    plt.tight_layout()
    plt.savefig(fig_dir / "composition_by_age_group.png", dpi=160)
    plt.close()

    # DBI heatmap age x device
    heat = scored.pivot_table(index="age_group", columns="primary_device", values="dbi", aggfunc="mean")
    save_heatmap(heat, "Mean DBI by age group × device", fig_dir / "dbi_heatmap_age_device.png", xlabel="Primary device", ylabel="Age group")

    # DBI by device and internet type
    dbi_by_device = scored.groupby("primary_device")["dbi"].mean().sort_values(ascending=False)
    save_bar(dbi_by_device, "Mean DBI by device", fig_dir / "dbi_by_device.png", ylabel="Mean DBI")

    dbi_by_net = scored.groupby("internet_type")["dbi"].mean().sort_values(ascending=False)
    save_bar(dbi_by_net, "Mean DBI by internet type", fig_dir / "dbi_by_internet_type.png", ylabel="Mean DBI")

    # Daily trends (DBI + n)
    fig = plt.figure(figsize=(10, 5))
    ax1 = fig.add_subplot(111)
    ax1.plot(daily["date"], daily["dbi_mean"], label="Mean DBI")
    ax1.set_ylabel("Mean DBI")
    ax1.set_title("Daily trends: mean DBI with sample size")
    ax1.tick_params(axis="x", rotation=30)

    ax2 = ax1.twinx()
    ax2.plot(daily["date"], daily["n"], linestyle="--", label="Daily n")
    ax2.set_ylabel("Daily sample size (n)")
    fig.tight_layout()
    fig.savefig(fig_dir / "daily_trends.png", dpi=160)
    plt.close(fig)

    return {
        "out_dir": str(out_dir),
        "figures_dir": str(fig_dir),
        "n_rows": int(len(scored)),
        "n_days": int(daily["date"].nunique()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Digital Balance Index (DBI) scoring pipeline")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--out", default="outputs", help="Outputs directory")
    parser.add_argument("--figures", default="reports/figures", help="Figures directory")
    args = parser.parse_args()

    res = run(args.input, args.out, args.figures)

    print("\nDone! DBI project outputs created.", flush=True)
    print(f"Outputs folder: {res['out_dir']}", flush=True)
    print(f"Figures folder: {res['figures_dir']}", flush=True)
    print(f"Rows scored: {res['n_rows']}", flush=True)
    print(f"Days covered: {res['n_days']}\n", flush=True)


if __name__ == "__main__":
    main()

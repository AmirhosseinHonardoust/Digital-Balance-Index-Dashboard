from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def save_bar(series: pd.Series, title: str, out_path: Path, xlabel: str = "", ylabel: str = "Count") -> None:
    plt.figure()
    series.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=160)
    plt.close()


def save_hist(series: pd.Series, title: str, out_path: Path, bins: int = 30, xlabel: str = "") -> None:
    plt.figure()
    plt.hist(series.dropna(), bins=bins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=160)
    plt.close()


def save_scatter(x: pd.Series, y: pd.Series, title: str, out_path: Path, xlabel: str, ylabel: str) -> None:
    plt.figure()
    plt.scatter(x, y, s=10, alpha=0.35)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=160)
    plt.close()


def save_heatmap(pivot: pd.DataFrame, title: str, out_path: Path, xlabel: str = "", ylabel: str = "") -> None:
    plt.figure(figsize=(8, 5))
    plt.imshow(pivot.values, aspect="auto")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(range(pivot.shape[1]), pivot.columns, rotation=30, ha="right")
    plt.yticks(range(pivot.shape[0]), pivot.index)
    plt.colorbar(label="Mean DBI")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=160)
    plt.close()

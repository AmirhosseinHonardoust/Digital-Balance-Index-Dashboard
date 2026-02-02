import sys
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import run as run_pipeline  # noqa: E402

st.set_page_config(page_title="DBI Dashboard", layout="wide")

st.title("Digital Balance Index (DBI) Dashboard")
st.caption("Composition-first analytics for daily screen time: balance, dominance, segments, and safe interpretation.")

DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "daily_internet_usage_by_age_group.csv"
OUT_DIR = PROJECT_ROOT / "outputs"
FIG_DIR = PROJECT_ROOT / "reports" / "figures"

with st.sidebar:
    st.header("Data & pipeline")
    uploaded = st.file_uploader("Upload CSV (optional)", type=["csv"])
    input_path = st.text_input("Or CSV path", value=str(DEFAULT_INPUT))
    run_btn = st.button("Run / Refresh Pipeline")

effective_input = Path(input_path)
if uploaded is not None:
    tmp = PROJECT_ROOT / "data" / "raw" / "uploaded.csv"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(uploaded.getbuffer())
    effective_input = tmp

if run_btn:
    with st.spinner("Running scoring pipeline..."):
        run_pipeline(input_path=str(effective_input), out_dir=str(OUT_DIR), figures_dir=str(FIG_DIR))
    st.success("✅ Done! Outputs and figures regenerated.")

cards_path = OUT_DIR / "metric_cards.json"
scored_path = OUT_DIR / "scored_rows.csv"
seg_path = OUT_DIR / "segment_summary.csv"
daily_path = OUT_DIR / "daily_summary.csv"

if not scored_path.exists():
    st.info("Run the pipeline from the sidebar to generate outputs.")
    st.stop()

cards = json.loads(cards_path.read_text(encoding="utf-8")) if cards_path.exists() else {}
scored = pd.read_csv(scored_path)
seg = pd.read_csv(seg_path) if seg_path.exists() else pd.DataFrame()
daily = pd.read_csv(daily_path) if daily_path.exists() else pd.DataFrame()

with st.sidebar:
    st.header("Filters")
    age = st.multiselect("Age group", sorted(scored["age_group"].unique().tolist()), default=sorted(scored["age_group"].unique().tolist()))
    dev = st.multiselect("Primary device", sorted(scored["primary_device"].unique().tolist()), default=sorted(scored["primary_device"].unique().tolist()))
    net = st.multiselect("Internet type", sorted(scored["internet_type"].unique().tolist()), default=sorted(scored["internet_type"].unique().tolist()))
    tiers = st.multiselect("DBI tier", ["Balanced", "Mixed", "Skewed"], default=["Balanced", "Mixed", "Skewed"])

f = scored[
    scored["age_group"].isin(age)
    & scored["primary_device"].isin(dev)
    & scored["internet_type"].isin(net)
    & scored["dbi_tier"].isin(tiers)
].copy()

tab_overview, tab_segments, tab_composition, tab_trends, tab_notes = st.tabs(
    ["Overview", "Segments", "Composition", "Trends", "Decision Safety Notes"]
)

with tab_overview:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Rows", len(f))
    c2.metric("Avg total (hrs)", round(f["total_screen_time"].mean(), 2))
    c3.metric("Avg DBI", round(f["dbi"].mean(), 3))
    c4.metric("Balanced %", round((f["dbi_tier"] == "Balanced").mean() * 100, 1))
    c5.metric("High-load & Skewed %", round(f["flag_highload_skewed"].mean() * 100, 1))

    st.subheader("Total screen time vs DBI (quadrants)")
    st.plotly_chart(
        px.scatter(
            f,
            x="total_screen_time",
            y="dbi",
            color="dbi_tier",
            hover_data=["age_group", "primary_device", "internet_type", "dominant_category"],
        ),
        width="stretch",
    )

    st.subheader("DBI distribution")
    st.plotly_chart(px.histogram(f, x="dbi", nbins=30, color="dbi_tier"), width="stretch")

with tab_segments:
    st.subheader("Top segments by High-load & Skewed rate")
    if not seg.empty:
        st.dataframe(seg.head(30), width="stretch", hide_index=True)
        st.caption("highload_skewed_rate is the % within each age_group × device × internet_type segment.")
    else:
        st.info("Segment summary not found. Run pipeline.")

    st.subheader("Mean DBI by device and internet type")
    g = f.groupby(["primary_device", "internet_type"])["dbi"].mean().reset_index()
    st.plotly_chart(px.bar(g, x="primary_device", y="dbi", color="internet_type", barmode="group"), width="stretch")

with tab_composition:
    st.subheader("Average composition (shares) by age group")
    comp = f.groupby("age_group")[["p_social", "p_work", "p_entertainment"]].mean().reset_index()
    comp_m = comp.melt(id_vars=["age_group"], var_name="component", value_name="share")
    comp_m["component"] = comp_m["component"].map({
        "p_social": "Social",
        "p_work": "Work/Study",
        "p_entertainment": "Entertainment",
    })
    st.plotly_chart(px.bar(comp_m, x="age_group", y="share", color="component", barmode="stack"), width="stretch")

    st.subheader("Dominant category (counts)")
    dom = f["dominant_category"].value_counts().reset_index()
    dom.columns = ["category", "count"]
    st.plotly_chart(px.bar(dom, x="category", y="count"), width="stretch")

with tab_trends:
    st.subheader("Daily trends (aggregated)")
    if not daily.empty:
        daily["date"] = pd.to_datetime(daily["date"])
        st.plotly_chart(px.line(daily, x="date", y="dbi_mean", title="Mean DBI by date"), width="stretch")
        st.plotly_chart(px.line(daily, x="date", y="total_mean", title="Mean total screen time by date"), width="stretch")
        st.plotly_chart(px.bar(daily, x="date", y="n", title="Daily sample size (n)"), width="stretch")
        st.caption("These are daily aggregates across unique users, not per-person time series.")
    else:
        st.info("Daily summary not found. Run pipeline.")

with tab_notes:
    st.markdown(
        """
### How to interpret DBI safely
- **DBI is descriptive**, not a wellbeing score. It measures how evenly time is split across categories.
- A high DBI does not mean “good”; a low DBI does not mean “bad”. It means **more dominated** by a category.
- This dataset is observational. Avoid causal language such as “WiFi causes entertainment”.

### Strong interpretations
- Composition differences across segments (shares) are typically more stable than raw totals.
- “High load & Skewed” can be used as an attention flag to investigate further.

### Weak interpretations
- Any health outcome inference (not present in the dataset).
- Claiming a device/internet type *causes* a pattern.
        """.strip()
    )

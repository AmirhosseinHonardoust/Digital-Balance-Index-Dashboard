<p align="center">
  <h1 align="center">Digital Balance Index (DBI) Dashboard </h1>
    <p align="center">
<div align="center">
   
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Wrangling-brown)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-green)
![Analytics](https://img.shields.io/badge/Focus-Behavioral%20Analytics-purple)
![Metric](https://img.shields.io/badge/Metric-DBI%20%28Digital%20Balance%20Index%29-yellow)
![License](https://img.shields.io/badge/License-MIT-lime)
   
</div>
   
---
 
A portfolio-grade analytics project that turns raw “hours spent” into **composition-first behavioral insights**.

Most screen-time analyses stop at **totals** (“people spend 8 hours/day”).  
This project focuses on *how that time is distributed* across:
- **Social**
- **Work/Study**
- **Entertainment**

It ships:
- a reproducible scoring pipeline (`python -m src.pipeline`)
- clean exported datasets + figures
- a Streamlit dashboard for interactive exploration across **age_group**, **primary_device**, and **internet_type**

---

## Dataset (source + thanks)
This project uses the Kaggle dataset:

- **Daily Internet Usage Statistics by Age Group** by **jayjoshi37**
- Dataset URL: https://www.kaggle.com/datasets/jayjoshi37/daily-internet-usage-statistics-by-age-group

Thanks to the dataset author and Kaggle for making the data available.

---

## Why this project exists
### The problem with “total hours”
Two users can both have **10 hours/day** of screen time, but with completely different patterns:
- One: mostly Work/Study (structured use)
- Another: mostly Social/Entertainment (dominant categories)

Totals alone can’t describe behavior.  
**Composition metrics** can.

### The core idea
For each record, we compute:
1) **Shares** of total screen time for each category  
2) **DBI** (Digital Balance Index): how evenly those shares are distributed  
3) **Dominance**: how strongly one category “owns” the day  
4) Practical tiers and a flag: **High-load & Skewed**

---

## What’s inside (pipeline + dashboard)
### Pipeline outputs
After running the pipeline you get:

- `outputs/scored_rows.csv`  
  Original data + engineered features:
  - shares (`p_social`, `p_work`, `p_entertainment`)
  - `dbi`, `dominance`, `dominant_category`
  - tiers (`dbi_tier`, `load_tier`)
  - risk flag (`flag_highload_skewed`)

- `outputs/segment_summary.csv`  
  Aggregated statistics by:
  - `age_group × primary_device × internet_type`

- `outputs/daily_summary.csv`  
  Daily aggregates:
  - mean DBI / mean total / sample size (n) per day

- `outputs/metric_cards.json`  
  KPI cards + thresholds and validation checks

- `reports/figures/`  
  All figures used in this README

### Dashboard
The Streamlit dashboard allows:
- filtering by age group, device, internet type, DBI tier
- exploring DBI distributions and segment comparisons
- safe interpretation notes (“decision safety”)

---

## Metrics (clear + reproducible)
Let:

- total = total_screen_time  
- social = social_media_hours  
- work = work_or_study_hours  
- ent = entertainment_hours  

### 1) Shares (composition)
- p_social = social / total  
- p_work = work / total  
- p_entertainment = ent / total  

These are proportions in [0, 1] and (when total > 0) they sum to ~1.

### 2) DBI (Digital Balance Index) 0 to 1
DBI uses **normalized Shannon entropy** over the three shares:

- H = - Σ (p_i * ln(p_i))  for i in {social, work, entertainment}
- DBI = H / ln(3)

Interpretation:
- **DBI ≈ 1.00** → time is distributed evenly (balanced composition)
- **DBI ≈ 0.00** → time is concentrated in one category (skewed composition)

Important note:
- DBI does **not** say “good” or “bad”
- DBI says “balanced” vs “dominated”

### 3) Dominance 0.33 to 1.00
- dominance = max(p_social, p_work, p_entertainment)

Interpretation:
- **dominance close to 1.0** → one category dominates
- **dominance close to 0.33** → near-even split

### 4) Practical tiers (used in outputs + dashboard)
DBI tiers:
- Balanced: DBI ≥ 0.80
- Mixed: 0.60–0.79
- Skewed: < 0.60

Load tiers (by quantiles of total screen time):
- Low / Medium / High based on P33 and P66

Flag:
- `flag_highload_skewed = 1` if **load_tier == High** AND **dbi_tier == Skewed**

This is intentionally phrased as “attention-worthy,” not “harmful.”

---

## Quickstart
### 1) Install
```bash
python -m venv .venv
# Windows:
#   .venv\Scripts\activate
# macOS/Linux:
#   source .venv/bin/activate
pip install -r requirements.txt
````

### 2) Run the pipeline

```bash
python -m src.pipeline --input data/raw/daily_internet_usage_by_age_group.csv
```

You should see a Done message and the output folders printed.

### 3) Launch the dashboard

```bash
streamlit run app/app.py
```

---

## Project structure

```text
digital-balance-index-dashboard/
  data/
    raw/
    processed/
  outputs/
  reports/
    figures/
  src/
    io.py
    validate.py
    scoring.py
    aggregates.py
    reporting.py
    pipeline.py
  app/
    app.py
  README.md
  requirements.txt
```

---

# Figures (with interpretation)

Below are the key plots generated by the pipeline.

---

## 1) Composition by age group (mean shares)

<img width="1024" height="768" alt="composition_by_age_group" src="https://github.com/user-attachments/assets/9ae7137c-576b-4d9e-af62-3ae472c6cfd2" />

### What this chart shows

Each bar is an age group.
The bar stacks to 1.0 (100% of total screen time), split into:

* Social
* Work/Study
* Entertainment

This answers:

* Do age groups differ more by **total time**, or by **how time is distributed**?

### How to read it correctly

* Look for **relative differences** in shares (e.g., Work/Study share slightly higher in one group).
* A similar composition across groups suggests:

  * differences may lie more in *total screen time* than *usage mix*.

### Common pitfalls

* Don’t interpret this as “who uses more.”
  This plot is **composition**, not absolute hours.
* A group can have the same composition but different total hours.

---

## 2) DBI distribution

<img width="1024" height="768" alt="dbi_distribution" src="https://github.com/user-attachments/assets/45e7e128-fef9-4e0c-a7c8-d065f1921212" />

### What this chart shows

A histogram of DBI values across all records.

### Why it matters

This is your “macro fingerprint”:

* If DBI is mostly high → usage is generally mixed/balanced in composition.
* If DBI has a heavy low tail → many users have dominated usage (one category owns most of the day).

### Practical interpretation

* High DBI dominance suggests many “mixed days,” not necessarily “low usage.”
* A low-DBI tail is where you’d investigate dominant categories:

  * dominated by Social?
  * dominated by Entertainment?
  * or dominated by Work/Study?

---

## 3) Total screen time vs DBI (composition vs load)

<img width="1024" height="768" alt="total_vs_dbi_scatter" src="https://github.com/user-attachments/assets/747779b8-a46f-49c6-a25c-c667eb88bde8" />

### What this chart shows

Each dot is a record:

* x-axis: total screen time (hours)
* y-axis: DBI (0–1)

### The key insight

This separates two different questions:

* **How much?** (load)
* **How distributed?** (composition)

### The useful “quadrants”

Even without drawing lines, you can think in quadrants:

* **High total + High DBI**
  Heavy usage, but spread across categories (mixed day)

* **High total + Low DBI**
  Heavy usage, dominated by one category (attention-worthy)

* **Low total + High DBI**
  Light usage, balanced composition

* **Low total + Low DBI**
  Light usage, but concentrated (short + focused)

### Decision safety note

This plot is descriptive: it suggests where to *look*, not what to *diagnose*.

---

## 4) Daily trends: mean DBI with sample size

<img width="1600" height="800" alt="daily_trends" src="https://github.com/user-attachments/assets/f919b24d-1512-4885-a3a8-322ee3965392" />

### What this chart shows

* Solid line: daily mean DBI
* Dashed line: sample size (n) that day

### Why sample size is plotted

Because daily means are only meaningful if daily n is stable.

* If n swings sharply, the mean can swing even if behavior didn’t change.

### What you can and cannot conclude

Reasonable:

* “DBI is fairly stable across dates.”
* “Some days show deviations, but sample size should be checked.”

Not reasonable:

* “Behavior changed over time for the same people.”
  This dataset is not a per-person time series; it’s a collection of records by date.

---

## 5) Mean DBI by primary device

<img width="1024" height="768" alt="dbi_by_device" src="https://github.com/user-attachments/assets/5ee1e36e-7cab-4e23-9102-1b061a5964ac" />

### What this chart shows

Average DBI per primary device category.

### What it’s useful for

* Quick comparison: are some devices associated with more balanced composition?

### How to interpret cautiously

* Small differences can be real or just sample noise.
* Device does not “cause” DBI differences; it’s an association.

A strong follow-up is to check:

* DBI distribution by device (not just means)
* segment breakdown: age group × device

---

## 6) Mean DBI by internet type

<img width="1024" height="768" alt="dbi_by_internet_type" src="https://github.com/user-attachments/assets/4e34b9a1-b4e8-41b1-8573-0f04ad97fecb" />

### What this chart shows

Average DBI for WiFi vs Mobile Data.

### What it suggests (carefully)

If values are similar:

* connectivity context may not be a major driver of composition balance

If values differ:

* could reflect behavior contexts (e.g., mobile data used on the go)

Again: this is association, not causation.

---

## 7) Mean DBI heatmap: age group × primary device

<img width="1280" height="800" alt="dbi_heatmap_age_device" src="https://github.com/user-attachments/assets/513b3e3a-6038-4f2b-916c-549bf13128b5" />

### What this chart shows

Mean DBI for each (age_group, primary_device) combination.

### Why it’s powerful

This reveals interaction patterns that “mean by device” hides:

* a device might look balanced overall,
* but show different balance depending on age group.

### How to use it

* Spot extremes (highest and lowest cells)
* Use segment_summary.csv to confirm:

  * n per segment
  * composition means
  * high-load & skewed rate

---

## Decision Safety (how to present this responsibly)

This project is designed for **safe analytics**:

* DBI is not a mental health score.
* DBI is not a productivity score.
* DBI is not a diagnosis.

Recommended language:

* “composition pattern”
* “dominant category”
* “balanced vs skewed distribution”
* “attention-worthy segment”

Avoid language like:

* “addicted”
* “harmful”
* “unhealthy”
* “caused by WiFi/device”

---

## Reproducibility & validation

The pipeline includes:

* schema validation (required columns)
* identity validation: total ≈ social + work + entertainment
* consistent export paths and figures

---

## Roadmap (optional upgrades)

If you want to level this up further:

* Add bootstrap confidence intervals for segment means (DBI/total)
* Add “What-if composition simulator” (move minutes between categories → new DBI)
* Add dominance + category-specific deep dives
* Add segment stability checks (min n threshold)

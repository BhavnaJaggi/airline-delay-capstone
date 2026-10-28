# U.S. Airline Delays, Load Factor and Demand Forecasting (QM 640 Capstone)

**Student:** Bhavna Jaggi | **Mentor:** Keya Choudhury Ganguli | **Course:** QM 640 Data Analytics Capstone, Walsh College

This repository holds the data pipeline, analysis notebooks and results behind the QM 640 interim report.
Everything uses **free, public U.S. Bureau of Transportation Statistics (BTS) TranStats data**. No Kaggle data and no synthetic data are used.

## Research questions

| RQ | Question | Main method |
|----|----------|-------------|
| RQ1 | Which flight characteristics (time of day, day of week, month, carrier, airports, distance, prior-month load factor) are associated with a flight arriving 15+ minutes late? | Logistic regression (inference) with random forest / XGBoost + SHAP as comparison |
| RQ2 | Is route-month load factor associated with the route-month late-arrival rate? | Pearson / Spearman correlation, OLS regression with robustness checks |
| RQ3 | Are cancellation rates associated with the operating profile of carrier-airport clusters? | k-means clustering, then chi-square, Cramer's V, Kruskal-Wallis |
| RQ4 | Does an LSTM forecaster beat a SARIMA baseline for monthly route passenger demand? | Seasonal-naive vs SARIMA vs LSTM, MAE / RMSE / MASE, paired tests |

## Repository structure

```
airline-delay-capstone/
|-- README.md                  <- this file
|-- requirements.txt           <- Python packages
|-- .gitignore                 <- keeps the huge raw monthly files out of git
|-- data/
|   |-- README.md              <- data sources, exact download links, data dictionary
|   |-- raw/
|   |   |-- otp/               <- put the 24 monthly On-Time files (2024 and 2025) here (NOT committed)
|   |   `-- t100_segment/      <- put the T-100 Segment files (2022 to 2026) here (NOT committed)
|   |-- raw_sample/            <- 100,000-row random sample of the raw On-Time data (committed)
|   `-- processed/             <- cleaned analysis tables written by notebook 01 (small ones committed)
|-- notebooks/                 <- run in this order
|   |-- 00_sample_size.ipynb               sample-size calculation for every RQ
|   |-- 01_download_clean.ipynb            load, audit, clean, join (cleaning log)
|   |-- 02_eda.ipynb                       exploratory data analysis (12 figures)
|   |-- 03_rq1_late_arrival.ipynb          RQ1 models
|   |-- 04_rq2_load_factor_delay.ipynb     RQ2 correlation and regression
|   |-- 05_rq3_clusters_cancellation.ipynb RQ3 clustering and tests
|   `-- 06_rq4_forecasting.ipynb           RQ4 forecasting comparison
|-- scripts/
|   |-- config.py              <- every study setting (years, seeds, thresholds, sample-size inputs)
|   |-- bts_io.py              <- readers for the two BTS tables (checks headers, stops on missing fields)
|   |-- download_bts_otp.py    <- optional helper to download the monthly On-Time files
|   |-- run_all.py             <- runs notebooks 00-06 in order
|   |-- metrics.py, plot_style.py, results_store.py
|-- outputs/
|   |-- figures/               <- every figure used in the report (PNG, 220 dpi)
|   |-- tables/                <- every table used in the report (CSV)
|   `-- results.json           <- every number quoted in the report, written by the notebooks
`-- report/                    <- interim report (docx / pdf)
```

## How to reproduce

1. **Get Python 3.10 or newer**, then install packages:
   ```bash
   python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   On a Mac, XGBoost also needs the OpenMP library: `brew install libomp`.
2. **Download the data** (free, no account needed). Exact links and field lists are in [`data/README.md`](data/README.md).
   * On-Time Performance, calendar years **2024 and 2025**, 24 monthly files -> `data/raw/otp/`
     (`python scripts/download_bts_otp.py` or use the BTS form). The years are set in `scripts/config.py` (`OTP_YEARS`);
     use `[2025]` alone if your computer has little memory (two years is about 14 million flights, so 16 GB of RAM is comfortable).
   * T-100 Domestic Segment (All Carriers), 2022 up to the latest published month of 2026, all fields -> `data/raw/t100_segment/`
3. **Run everything**:
   ```bash
   python scripts/run_all.py          # or open the notebooks in JupyterLab and run 00 -> 06 in order
   ```
   Running time depends on your computer; notebooks 01, 03 and 06 are the slowest.
4. Figures, tables and `outputs/results.json` are regenerated. Every number in the report comes from `results.json`.

Every random process uses `RANDOM_STATE = 42` (set in `scripts/config.py`), so reruns on the same data give the same results.
Study settings (year, number of routes, thresholds) are all in `scripts/config.py`.

## Data availability statement

The raw data are public U.S. government data and are **not redistributed here** because two years of flight-level On-Time files are several gigabytes
uncompressed and far larger than GitHub's file-size limits. Instead the repository contains (a) a 100,000-row random sample of the raw On-Time data
(`data/raw_sample/`), (b) the cleaned and aggregated analysis tables (`data/processed/`), and (c) the exact download links, field lists and
scripts needed to recreate the full raw files. Source: U.S. Department of Transportation, Bureau of Transportation Statistics, TranStats (https://www.transtats.bts.gov).

## Running in Google Colab instead

Colab works with these notebooks: upload the repository folder to Google Drive, mount Drive, `%cd` into the repository, run
`!pip install -r requirements.txt`, then open the notebooks. No Kaggle account or Kaggle notebook is needed.
# airline-delay-capstone

# U.S. Airline Delays, Load Factor and Demand Forecasting (QM 640 Capstone)

**Student:** Bhavna Jaggi | **Mentor:** Keya Choudhury Ganguli | **Course:** QM 640 Data Analytics Capstone, Walsh College

This repository holds the data, code, database, models, deployment prototype and results behind the QM 640 **interim report** and **final report**
(both in `report/`). Everything uses **free, public U.S. Bureau of Transportation Statistics (BTS) TranStats data**. No Kaggle data and no synthetic data are used.

## Research questions

| RQ | Question | Main method |
|----|----------|-------------|
| RQ1 | Which flight characteristics (departure time block, day of week, month, carrier, airports, distance, prior-month load factor) are associated with a flight arriving 15+ minutes late, and how accurately can models predict it before departure compared with the historical on-time rates used today? | Logistic regression (inference) with random forest and XGBoost (tuned and default), SHAP, time-based check |
| RQ2 | Is route-month load factor associated with the route-month late-arrival rate? | Pearson / Spearman correlation, OLS with route-clustered errors, route-grouped holdout |
| RQ3 | Do carrier-airport operations fall into distinct groups, and do the groups differ in cancellation rate? | k-means, chi-square, Cramér's V, Kruskal-Wallis, bootstrap stability |
| RQ4 | Does an LSTM forecast monthly route passengers more accurately than SARIMA over a held-out 12 months? | Seasonal naive, exponential smoothing, SARIMA, LSTM; MAE / RMSE / MASE; paired tests |

## Repository structure

```
airline-delay-capstone/
|-- README.md, RUN_FINAL.md, requirements.txt
|-- data/
|   |-- raw/otp/            24 monthly On-Time Performance files, 2024-2025 (zipped, as downloaded)
|   |-- raw/t100_segment/   T-100 Domestic Segment files, 2022-2026 (zipped)
|   |-- raw_sample/         100,000-row random sample of the raw On-Time data
|   `-- processed/          analysis tables written by the notebooks (the Parquet file and the DuckDB database are rebuilt locally)
|-- notebooks/              run in this order
|   |-- 00_sample_size                  minimum sample size for every RQ
|   |-- 01_download_clean               load, audit, clean, join (cleaning log)
|   |-- 02_eda                          exploratory data analysis
|   |-- 03_rq1_late_arrival             RQ1 models, time-based check
|   |-- 04_rq2_load_factor_delay        RQ2 correlation and regression
|   |-- 05_rq3_clusters_cancellation    RQ3 clustering and tests
|   |-- 06_rq4_forecasting              RQ4 forecasting comparison
|   `-- 07_final_extensions             tuning, train/test table, risk deciles, current-practice benchmark, saves the scoring model
|-- scripts/                shared code (config, readers, metrics, features), database build and checks, run_all.py, run_final.py
|-- sql/schema.sql          DuckDB star-style schema (2 dimension tables, 3 fact tables, views)
|-- app/                    scoring module, Streamlit dashboard, FastAPI interface, saved model (app/model/)
|-- outputs/                figures (PNG), tables (CSV), results.json (every number quoted in the reports)
`-- report/                 interim and final reports (docx and pdf)
```

## How to reproduce

1. **Python 3.11 or 3.12**, then:
   ```bash
   python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   On a Mac, XGBoost also needs the OpenMP library: `brew install libomp`.
2. **Data.** The raw zipped files are already in `data/raw/`. To download them again, see [`data/README.md`](data/README.md) (exact links and field lists) or run `python scripts/download_bts_otp.py`.
3. **Run the analysis notebooks** (notebooks 01, 03 and 06 are the slowest):
   ```bash
   python scripts/run_all.py
   ```
4. **Run the final-report additions** (database, tuning, scoring model, example flights; about 15-40 minutes):
   ```bash
   python scripts/run_final.py
   ```
   See [`RUN_FINAL.md`](RUN_FINAL.md). This also writes `outputs/tables/environment.json` (computer and package versions).
5. **Try the deployment prototype:**
   ```bash
   streamlit run app/streamlit_app.py          # dashboard
   uvicorn app.api:app --port 8000             # programming interface; docs at http://127.0.0.1:8000/docs
   ```

Every random process uses `RANDOM_STATE = 42` (set in `scripts/config.py`), so reruns on the same data and package versions give the same results.

## Computer used for the reported results

Apple M4, 24 GB memory, 10 logical cores, central processing unit only (no graphics processing unit); Python 3.12.16. Package versions are in `outputs/tables/environment.json`.

## Data availability statement

The raw data are public U.S. government data from the U.S. Department of Transportation, Bureau of Transportation Statistics, TranStats (https://www.transtats.bts.gov).
The monthly files exactly as downloaded are included in `data/raw/` as `.zip` files, together with a 100,000-row sample, the aggregated analysis tables, the exact download links,
field lists and download script. The cleaned flight-level Parquet file (about 230 MB) and the DuckDB database are rebuilt by notebook 01 and `scripts/build_database.py`.

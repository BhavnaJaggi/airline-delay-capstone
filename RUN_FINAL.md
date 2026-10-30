# Final-report additions: how to run them

Everything below runs on your own computer, inside the project folder, with the virtual environment active.

```bash
cd ~/Downloads/airline-delay-capstone
source .venv/bin/activate
pip install -r requirements.txt          # adds duckdb, fastapi, uvicorn, streamlit, httpx, psutil
python scripts/run_final.py              # about 15-40 minutes; leave the laptop awake and plugged in
```

`run_final.py` does six things in order: records the computer used (`outputs/tables/environment.json`),
builds the DuckDB database (`data/processed/airline_delay.duckdb`), re-runs notebooks 03, 06 and 07,
checks 10 SQL queries against the pipeline results, saves the scoring-model files in `app/model/`, and scores two example flights for the report.

## Try the deployment prototype (optional, for screenshots)

```bash
streamlit run app/streamlit_app.py              # dashboard in the browser
uvicorn app.api:app --port 8000                 # programming interface; open http://127.0.0.1:8000/docs
```

## Publish

```bash
git add -A
git commit -m "Final report: database, tuned models, deployment prototype, new figures"
git push
```

The DuckDB file and the Parquet file are rebuilt by the scripts and are not committed.

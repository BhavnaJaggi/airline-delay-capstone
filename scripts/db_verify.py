"""Check the analytical database against the numbers reported from the pandas pipeline, and time typical queries.

    python scripts/db_verify.py

Every query below is plain SQL run through DuckDB. The 'pipeline value' column is read from outputs/results.json
(written by the notebooks); the check passes when SQL and the pipeline agree.
"""
import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import TAB, RESULTS_JSON               # noqa: E402
from build_database import connect                 # noqa: E402

R = json.load(open(RESULTS_JSON))
con = connect()
checks = []


def run(label, sql, pipeline_value, tol=1e-6):
    t = time.perf_counter()
    val = con.execute(sql).fetchone()[0]
    dt = time.perf_counter() - t
    ok = abs(float(val) - float(pipeline_value)) <= tol * max(1.0, abs(float(pipeline_value)))
    checks.append({"query": label, "sql_result": float(val), "pipeline_value": float(pipeline_value), "agrees": bool(ok), "seconds": round(dt, 3)})


run("Flights in the cleaned flight table", "SELECT COUNT(*) FROM flight", R["eda"]["n_flights"])
run("Operated flights", "SELECT SUM(operated) FROM flight", R["eda"]["n_operated"])
run("Late-arrival rate of operated flights (%)", "SELECT 100.0 * SUM(is_late) / SUM(operated) FROM flight", R["eda"]["late_rate_pct"], 1e-4)
run("Cancellation rate (%)", "SELECT 100.0 * SUM(cancelled) / COUNT(*) FROM flight", R["eda"]["cancel_rate_pct"], 1e-4)
run("Late-arrival rate in July 2024 (%)", "SELECT late_arrival_rate FROM v_monthly_performance WHERE year = 2024 AND month = 7", R["eda"]["monthly_late"]["2024-07"], 1e-3)
run("Route-months in the research question 2 table", "SELECT COUNT(*) FROM fact_route_month WHERE flights_operated >= 30 AND load_factor IS NOT NULL", R["rq2"]["n"])
run("Pearson correlation of load factor and late rate",
    "SELECT corr(load_factor, late_rate) FROM fact_route_month WHERE flights_operated >= 30 AND load_factor IS NOT NULL", R["rq2"]["pearson_r"], 1e-6)
run("Carrier-airport units in the research question 3 table", "SELECT COUNT(*) FROM fact_carrier_airport", R["rq3"]["units"])
run("Routes with monthly passengers (research question 4)", "SELECT COUNT(DISTINCT route) FROM fact_route_passengers", R["rq4"]["routes"])
run("Flights per carrier-airport unit, total", "SELECT SUM(flights_scheduled) FROM fact_carrier_airport", R["rq3"]["flights"])
out = pd.DataFrame(checks)
out.to_csv(TAB / "db_verification.csv", index=False)
print(out.to_string(index=False))
print("\nall checks agree:", bool(out["agrees"].all()))
con.close()

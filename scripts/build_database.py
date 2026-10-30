"""Build the analytical database (DuckDB) from the cleaned tables.

    python scripts/build_database.py

Creates data/processed/airline_delay.duckdb with dimension and fact tables (see sql/schema.sql) and prints
row counts. The 14-million-row flight table is not copied into the file: it is read from Parquet through a
view, which keeps the database file small (a few tens of megabytes) while queries stay in SQL.
"""
import sys
from pathlib import Path

import duckdb
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import PROCESSED, ROOT                    # noqa: E402
from labels import CARRIER_NAMES, AIRPORT_NAMES        # noqa: E402

DB = PROCESSED / "airline_delay.duckdb"
SCHEMA = ROOT / "sql" / "schema.sql"
PARQUET = PROCESSED / "otp_clean.parquet"


def connect(read_only=True):
    """Open the database and attach the flight-level Parquet file as the view `flight`."""
    con = duckdb.connect(str(DB), read_only=read_only)
    if PARQUET.exists():
        con.execute(f"CREATE OR REPLACE TEMP VIEW flight AS SELECT * FROM read_parquet('{PARQUET.as_posix()}')")
        con.execute("""CREATE OR REPLACE TEMP VIEW v_monthly_performance AS
            SELECT year, month, COUNT(*) AS flights_scheduled, SUM(operated) AS flights_operated,
                   100.0 * SUM(is_late) / SUM(operated) AS late_arrival_rate, 100.0 * SUM(cancelled) / COUNT(*) AS cancellation_rate
            FROM flight GROUP BY year, month""")
    return con


def build():
    if DB.exists():
        DB.unlink()
    con = duckdb.connect(str(DB))
    ddl = SCHEMA.read_text()
    con.execute("CREATE TEMP VIEW flight AS SELECT * FROM read_parquet('%s')" % PARQUET.as_posix())
    # tables first, the view that needs `flight` last
    parts = [p.strip() for p in ddl.split(";") if p.strip()]
    for p in parts:
        body = "\n".join(l for l in p.splitlines() if not l.strip().startswith("--")).strip()
        if body.upper().startswith("CREATE TABLE"):
            con.execute(body)

    # dimensions ---------------------------------------------------------------------------------
    car = con.execute("SELECT DISTINCT carrier_id, CAST(carrier AS VARCHAR) AS carrier_code FROM flight").df()
    car["carrier_name"] = car["carrier_code"].map(lambda c: CARRIER_NAMES.get(c, c))
    con.register("car", car)
    con.execute("INSERT INTO dim_carrier SELECT carrier_id, carrier_code, carrier_name FROM car")

    ap = pd.read_csv(PROCESSED / "airport_lookup.csv").rename(columns={"airport_id": "airport_id", "code": "airport_code"})
    ap["airport_name"] = ap["airport_code"].map(lambda c: AIRPORT_NAMES.get(c, c))
    con.register("ap", ap)
    con.execute("INSERT INTO dim_airport SELECT airport_id, airport_code, state, airport_name FROM ap")

    # facts --------------------------------------------------------------------------------------
    rm = pd.read_csv(PROCESSED / "route_month_analysis.csv")
    rm = rm[["year", "month", "carrier_id", "origin_id", "dest_id", "flights_scheduled", "flights_operated", "late", "cancelled",
             "passengers", "seats", "dep_performed", "dep_scheduled", "distance", "load_factor", "late_rate", "cancel_rate"]]
    con.register("rm", rm)
    con.execute("INSERT INTO fact_route_month SELECT * FROM rm")

    ca = pd.read_csv(PROCESSED / "carrier_airport.csv")
    ca = ca[["carrier_id", "origin_id", "flights_scheduled", "cancelled", "avg_load_factor", "mean_monthly_departures",
             "avg_distance", "seasonal_cv", "months", "cancel_rate"]]
    con.register("ca", ca)
    con.execute("INSERT INTO fact_carrier_airport SELECT * FROM ca")

    wide = pd.read_csv(PROCESSED / "route_monthly_passengers.csv")
    long = wide.melt(id_vars="period", var_name="route", value_name="passengers")[["route", "period", "passengers"]]
    long["period"] = pd.to_datetime(long["period"])
    con.register("long", long)
    con.execute("INSERT INTO fact_route_passengers SELECT route, CAST(period AS DATE), passengers FROM long")

    # the views over the Parquet file (flight, v_monthly_performance) are created at connection time by connect()
    con.close()
    con = duckdb.connect(str(DB), read_only=True)
    for t in ("dim_carrier", "dim_airport", "fact_route_month", "fact_carrier_airport", "fact_route_passengers"):
        print(f"{t:24s} {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:>10,} rows")
    con.close()
    print("database written:", DB, f"({DB.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    build()

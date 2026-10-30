-- Analytical database for the airline delay capstone (DuckDB).
-- Built by scripts/build_database.py from the cleaned tables written by notebook 01.
-- Star-style layout: two dimension tables, three fact tables, and views (one over the flight-level Parquet file).

CREATE TABLE dim_carrier (
    carrier_id    BIGINT PRIMARY KEY,      -- stable U.S. Department of Transportation airline identification number
    carrier_code  VARCHAR NOT NULL,        -- two-character reporting code (can be reused over time, hence not the key)
    carrier_name  VARCHAR NOT NULL
);

CREATE TABLE dim_airport (
    airport_id    BIGINT PRIMARY KEY,      -- stable airport identification number
    airport_code  VARCHAR NOT NULL,        -- three-letter location code
    state         VARCHAR,
    airport_name  VARCHAR
);

-- One row per carrier, route and month: the unit of analysis for research question 2.
CREATE TABLE fact_route_month (
    year INTEGER, month INTEGER,
    carrier_id BIGINT REFERENCES dim_carrier(carrier_id),
    origin_id  BIGINT REFERENCES dim_airport(airport_id),
    dest_id    BIGINT REFERENCES dim_airport(airport_id),
    flights_scheduled INTEGER, flights_operated INTEGER, late DOUBLE, cancelled INTEGER,
    passengers DOUBLE, seats DOUBLE, dep_performed DOUBLE, dep_scheduled DOUBLE, distance DOUBLE,
    load_factor DOUBLE,                    -- passengers / seats x 100
    late_rate DOUBLE,                      -- late arrivals / operated flights x 100
    cancel_rate DOUBLE,
    PRIMARY KEY (year, month, carrier_id, origin_id, dest_id)
);

-- One row per carrier and origin airport: the unit of analysis for research question 3.
CREATE TABLE fact_carrier_airport (
    carrier_id BIGINT REFERENCES dim_carrier(carrier_id),
    origin_id  BIGINT REFERENCES dim_airport(airport_id),
    flights_scheduled BIGINT, cancelled BIGINT,
    avg_load_factor DOUBLE, mean_monthly_departures DOUBLE, avg_distance DOUBLE, seasonal_cv DOUBLE, months INTEGER, cancel_rate DOUBLE,
    PRIMARY KEY (carrier_id, origin_id)
);

-- Monthly passengers for the 150 busiest routes (all carriers): research question 4.
CREATE TABLE fact_route_passengers (
    route VARCHAR, period DATE, passengers DOUBLE,
    PRIMARY KEY (route, period)
);

-- Flight-level table (14,080,680 rows). It stays in Parquet (columnar, compressed) and is exposed as a view,
-- so the database file stays small and every query still runs in SQL:
--   CREATE VIEW flight AS SELECT * FROM read_parquet('data/processed/otp_clean.parquet');

CREATE VIEW v_monthly_performance AS
SELECT year, month,
       COUNT(*)                                             AS flights_scheduled,
       SUM(operated)                                        AS flights_operated,
       100.0 * SUM(is_late) / SUM(operated)                 AS late_arrival_rate,
       100.0 * SUM(cancelled) / COUNT(*)                    AS cancellation_rate
FROM flight GROUP BY year, month;

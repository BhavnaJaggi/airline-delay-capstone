# Data sources and dictionary

All data come from the U.S. Bureau of Transportation Statistics (BTS) TranStats portal. Both tables are free and public.
Table names, table codes and field lists below were checked against the BTS TranStats pages; the pre-zipped file pattern is the one BTS normally uses, so if a link fails use the form instead.

## 1. Reporting Carrier On-Time Performance (1987-present)  -> RQ1, RQ2, RQ3
* Unit: one row per scheduled domestic flight, by the reporting (operating) carrier.
* Field-selection / download form: https://www.transtats.bts.gov/DL_SelectFields.asp?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr
* Table page: https://www.transtats.bts.gov/Tables.asp?QO_VQ=EFI
* Pre-zipped monthly files: `https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_<YEAR>_<MONTH>.zip`
* What to download: **all 12 months of 2024 and of 2025** (24 files; `OTP_YEARS` in `scripts/config.py`). Save the `.zip` (or `.csv`) files unchanged into `data/raw/otp/`; file names do not matter.

| Field (as in file) | Meaning | Type |
|---|---|---|
| Year, Month, DayofMonth, DayOfWeek, FlightDate | Calendar fields (DayOfWeek 1 = Monday) | integer / date |
| Reporting_Airline, DOT_ID_Reporting_Airline | Carrier code and stable DOT carrier ID | text / integer ID |
| Flight_Number_Reporting_Airline | Flight number | integer |
| OriginAirportID, Origin, OriginState | Origin airport (stable ID, IATA code, state) | integer ID / text |
| DestAirportID, Dest, DestState | Destination airport | integer ID / text |
| CRSDepTime, DepTimeBlk | Scheduled departure time (hhmm) and its hourly block | integer / text |
| DepDelay, DepDel15 | Departure delay (minutes) and 15-minute indicator (**not used as a predictor: leakage**) | numeric / 0-1 |
| ArrDelay | Arrival delay in minutes (negative = early) | numeric |
| ArrDel15 | 1 if arrival delay >= 15 minutes (RQ1 and RQ2 outcome) | 0-1 |
| Cancelled, CancellationCode | Cancelled flag (RQ3 outcome) and reason code (A carrier, B weather, C NAS, D security) | 0-1 / text |
| Diverted | Diverted flag | 0-1 |
| CRSElapsedTime, Distance | Scheduled elapsed time and distance (miles) | numeric |
| CarrierDelay, WeatherDelay, NASDelay, SecurityDelay, LateAircraftDelay | Delay minutes by cause; only filled for flights delayed 15+ minutes | numeric |

## 2. T-100 Domestic Segment (All Carriers)  -> RQ2 (load factor), RQ3 (cluster features), RQ4 (monthly passengers)
* Unit: one row per carrier x non-stop segment x aircraft type x month.
* Field-selection / download form: https://transtats.bts.gov/DL_SelectFields.asp?gnoyr_VQ=GEE&QO_fu146_anzr=Nv4%20Pn44vr45
* Field list: https://transtats.bts.gov/Fields.asp?gnoyr_VQ=GEE
* What to download: one file per year **2022, 2023, 2024, 2025 and 2026** (filter *Year*, all months available, tick **all fields**; at least those below). 2026 is only published up to a recent month; that is fine, the notebook drops a partly published last month.
  Save into `data/raw/t100_segment/`. (Make sure you pick *All Carriers*, GEE, not the *U.S. Carriers* table, FIM.)

| Field | Meaning | Type |
|---|---|---|
| Year, Month | Calendar fields | integer |
| UniqueCarrier, AirlineID | Carrier code and stable DOT airline ID (matches `DOT_ID_Reporting_Airline`) | text / integer ID |
| OriginAirportID, Origin, DestAirportID, Dest | Segment end points (stable IDs match the On-Time file) | integer ID / text |
| DepScheduled, DepPerformed | Departures scheduled / performed in the month | integer |
| Seats | Available seats | integer |
| Passengers | Passengers transported on the segment | integer |
| Distance | Distance between airports (miles) | numeric |
| Class | Service class; **F = scheduled passenger service** (the only class kept) | text |
| AircraftGroup, AircraftType, AircraftConfig | Aircraft columns (rows are split by aircraft; the notebook sums them) | integer |

Load factor used in this project = Passengers / Seats x 100, computed after summing aircraft-type rows. Values above 100 % are treated as invalid.

## 3. Files produced by the notebooks (`data/processed/`)
| File | Content | Used for |
|---|---|---|
| `otp_clean.parquet` | cleaned flight-level table (not committed, rebuilt by notebook 01) | RQ1, EDA |
| `rq1_sample.csv.gz` | random modelling sample of flights with features | RQ1 |
| `route_month_analysis.csv` | route-month late rate joined to load factor | RQ2 |
| `carrier_airport.csv` | carrier-airport operating profile and cancellation counts | RQ3 |
| `route_monthly_passengers.csv` | monthly passengers, busiest routes, 2022 to the latest published month | RQ4 |
| `airport_lookup.csv` | airport ID to code and state | labels |

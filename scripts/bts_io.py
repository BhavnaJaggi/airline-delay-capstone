"""Readers for the two BTS TranStats tables used in this project.

* Reporting Carrier On-Time Performance (flight level)   -> read_otp()
* T-100 Domestic Segment, All Carriers (carrier x segment x month) -> read_t100()

BTS uses different header styles for different tables (e.g. 'Reporting_Airline'
in On-Time files vs 'AIRLINE_ID' / 'DEPARTURES_PERFORMED' in T-100 files), so
headers are normalised (lower-case, letters+digits only) and mapped to ONE set
of internal names. If a required field is missing the loader stops with a
message that lists exactly what is missing - it never guesses.
"""
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

# internal name -> accepted normalised header aliases ------------------------
OTP_FIELDS = {
    "year": ["year"], "month": ["month"], "day_of_month": ["dayofmonth"],
    "day_of_week": ["dayofweek"], "flight_date": ["flightdate"],
    "carrier": ["reportingairline", "uniquecarrier", "carrier"],
    "carrier_id": ["dotidreportingairline", "airlineid"],
    "flight_number": ["flightnumberreportingairline", "flightnum"],
    "origin_id": ["originairportid"], "origin": ["origin"], "origin_state": ["originstate"],
    "dest_id": ["destairportid"], "dest": ["dest"], "dest_state": ["deststate"],
    "crs_dep_time": ["crsdeptime"], "dep_time_blk": ["deptimeblk"],
    "dep_delay": ["depdelay"], "dep_del15": ["depdel15"],
    "crs_arr_time": ["crsarrtime"], "arr_delay": ["arrdelay"], "arr_del15": ["arrdel15"],
    "cancelled": ["cancelled"], "cancellation_code": ["cancellationcode"],
    "diverted": ["diverted"], "crs_elapsed": ["crselapsedtime"], "distance": ["distance"],
    "carrier_delay": ["carrierdelay"], "weather_delay": ["weatherdelay"],
    "nas_delay": ["nasdelay"], "security_delay": ["securitydelay"],
    "late_aircraft_delay": ["lateaircraftdelay"],
}
OTP_REQUIRED = ["year", "month", "day_of_week", "flight_date", "carrier", "carrier_id",
                "origin_id", "origin", "dest_id", "dest", "crs_dep_time", "dep_time_blk",
                "arr_delay", "arr_del15", "cancelled", "diverted", "distance"]

T100_FIELDS = {
    "year": ["year"], "month": ["month"],
    "carrier": ["uniquecarrier"], "carrier_id": ["airlineid"],
    "origin_id": ["originairportid"], "origin": ["origin"],
    "dest_id": ["destairportid"], "dest": ["dest"],
    "dep_scheduled": ["departuresscheduled", "depscheduled"],
    "dep_performed": ["departuresperformed", "depperformed"],
    "seats": ["seats"], "passengers": ["passengers"], "distance": ["distance"],
    "service_class": ["class"],
    # optional: rows are split by aircraft, so these make the duplicate check exact
    "aircraft_group": ["aircraftgroup"], "aircraft_type": ["aircrafttype"], "aircraft_config": ["aircraftconfig"],
}
T100_REQUIRED = ["year", "month", "carrier_id", "origin_id", "dest_id",
                 "dep_performed", "seats", "passengers", "distance", "service_class"]


def _norm(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def _column_map(header, fields):
    """Map the file's real headers to internal names. Returns {real_header: internal}."""
    by_norm = {}
    for real in header:
        by_norm.setdefault(_norm(real), real)
    mapping = {}
    for internal, aliases in fields.items():
        for a in aliases:
            if a in by_norm:
                mapping[by_norm[a]] = internal
                break
    return mapping


def _open_csv(path):
    """Yield (name, file-like) for a .csv or for the first .csv inside a .zip."""
    path = Path(path)
    if path.suffix.lower() == ".zip":
        zf = zipfile.ZipFile(path)
        csvs = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csvs:
            raise ValueError(f"No CSV inside {path.name}")
        return csvs[0], zf.open(csvs[0])
    return path.name, open(path, "rb")


def _read_one(path, fields, required, dtype_hint=None):
    name, fh = _open_csv(path)
    header = pd.read_csv(fh, nrows=0).columns.tolist()
    fh.close()
    cmap = _column_map(header, fields)
    missing = [r for r in required if r not in cmap.values()]
    if missing:
        raise ValueError(
            f"{Path(path).name}: required fields not found: {missing}. "
            f"Re-download the file with those fields ticked. Headers seen: {header[:12]}...")
    name, fh = _open_csv(path)
    df = pd.read_csv(fh, usecols=list(cmap.keys()), low_memory=False, dtype=dtype_hint)
    fh.close()
    return df.rename(columns=cmap)


def list_files(folder):
    folder = Path(folder)
    return sorted([p for p in folder.iterdir() if p.suffix.lower() in (".zip", ".csv")])


def read_otp(folder, years=None, verbose=True):
    """Read every On-Time file in `folder`; keep only the calendar `years` (int or list). Returns (df, inventory)."""
    if isinstance(years, int):
        years = [years]
    frames, inventory = [], []
    files = list_files(folder)
    if not files:
        raise FileNotFoundError(f"No .zip/.csv files in {folder}. See README for download steps.")
    for p in files:
        d = _read_one(p, OTP_FIELDS, OTP_REQUIRED)
        n_raw = len(d)
        if years is not None:
            d = d[d["year"].isin(years)]
        inventory.append({"file": p.name, "rows_in_file": n_raw, "rows_kept": len(d),
                          "periods": sorted((d["year"].astype(int) * 100 + d["month"].astype(int)).unique().tolist())})
        # compact dtypes (two years of flights is ~14 million rows, so memory matters)
        d = d.copy()
        d["flight_date"] = pd.to_datetime(d["flight_date"])
        for c in d.columns:
            if str(d[c].dtype).startswith("int"):
                d[c] = pd.to_numeric(d[c], downcast="integer")
        for c in ("carrier", "origin", "dest", "origin_state", "dest_state", "dep_time_blk",
                  "cancellation_code"):
            if c in d.columns:
                d[c] = d[c].astype("category")
        for c in d.columns:
            if d[c].dtype == "float64":
                d[c] = d[c].astype("float32")
        frames.append(d)
        if verbose:
            print(f"  read {p.name}: {n_raw:,} rows, kept {len(d):,}")
    # Give every month the SAME category set so pd.concat keeps compact 'category'
    # columns instead of falling back to memory-hungry text columns.
    cat_cols = [c for c in frames[0].columns if str(frames[0][c].dtype) == "category"]
    for c in cat_cols:
        union = sorted(set().union(*[set(f[c].cat.categories) for f in frames]))
        for f in frames:
            f[c] = f[c].cat.set_categories(union)
    df = pd.concat(frames, ignore_index=True)
    return df, pd.DataFrame(inventory)


def read_t100(folder, first_year=None, last_year=None, verbose=True):
    """Read every T-100 Segment file in `folder`. Returns (df, inventory)."""
    frames, inventory = [], []
    files = list_files(folder)
    if not files:
        raise FileNotFoundError(f"No .zip/.csv files in {folder}. See README for download steps.")
    for p in files:
        d = _read_one(p, T100_FIELDS, T100_REQUIRED)
        n_raw = len(d)
        if first_year is not None:
            d = d[(d["year"] >= first_year) & (d["year"] <= last_year)]
        inventory.append({"file": p.name, "rows_in_file": n_raw, "rows_kept": len(d),
                          "years": sorted(d["year"].unique().tolist())})
        frames.append(d)
        if verbose:
            print(f"  read {p.name}: {n_raw:,} rows, kept {len(d):,}")
    return pd.concat(frames, ignore_index=True), pd.DataFrame(inventory)

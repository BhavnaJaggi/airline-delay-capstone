"""Feature construction for the late-arrival models (research question 1).

The same function is used by notebook 07 (train/test comparison and tuning) and by the deployment
prototype in app/, so the model sees identical columns in training and in use.

Only information known before departure is used (no leakage):
month, weekday, scheduled departure block, distance, carrier, origin, destination and the
previous month's route load factor.
"""
import numpy as np
import pandas as pd

FACTOR_SPEC = {
    "Month": ("month_c", "month"),
    "Day of week": ("dow_c", "dow"),
    "Scheduled departure block": ("dep_time_blk", "blk"),
    "Carrier": ("carrier", "carr"),
    "Origin airport": ("origin_g", "orig"),
    "Destination airport": ("dest_g", "dest"),
}


def prepare_frame(df, top_origin, top_dest, lf_median):
    """Add the engineered columns to a frame of flights (training or new flights)."""
    df = df.copy()
    df["origin_g"] = df["origin"].where(df["origin"].isin(top_origin), "Other")
    df["dest_g"] = df["dest"].where(df["dest"].isin(top_dest), "Other")
    df["month_c"] = df["month"].astype(int).astype(str).str.zfill(2)
    df["dow_c"] = df["day_of_week"].astype(int).astype(str)
    df["distance_k"] = df["distance"] / 1000.0                       # per 1,000 miles
    df["lf_prev_missing"] = df["lf_prev"].isna().astype(int)
    df["lf_prev_10"] = (df["lf_prev"].fillna(lf_median) - lf_median) / 10   # per +10 percentage points
    return df


def fit_design(df, top_airports):
    """Training-time construction. Returns X, y, and the specification needed to rebuild X for new flights."""
    df = df.dropna(subset=["is_late", "distance", "carrier", "origin", "dest", "dep_time_blk"]).reset_index(drop=True)
    y = df["is_late"].astype(int).values
    top_o = list(df["origin"].value_counts().head(top_airports).index)
    top_d = list(df["dest"].value_counts().head(top_airports).index)
    lf_med = float(df["lf_prev"].median())
    df = prepare_frame(df, top_o, top_d, lf_med)

    blocks, refs, levels = {}, {}, {}
    for name, (col, pre) in FACTOR_SPEC.items():
        s = df[col].astype(str)
        ref = s.value_counts().index[0]                               # reference level = most common level
        d = pd.get_dummies(s, prefix=pre, dtype="float32")
        blocks[name] = d.drop(columns=f"{pre}_{ref}")
        refs[name], levels[name] = ref, sorted(s.unique().tolist())
    blocks["Route distance"] = df[["distance_k"]].astype("float32")
    blocks["Prior-month load factor"] = df[["lf_prev_10", "lf_prev_missing"]].astype("float32")
    X = pd.concat(list(blocks.values()), axis=1)
    X = X.loc[:, X.std() > 0]
    col_to_factor = {c: n for n, b in blocks.items() for c in b.columns if c in X.columns}
    spec = {"columns": list(X.columns), "col_to_factor": col_to_factor, "reference": refs, "levels": levels,
            "top_origin": top_o, "top_dest": top_d, "lf_median": lf_med}
    return df, X, y, spec


def transform(df_new, spec):
    """Build the design matrix for new flights using a saved specification."""
    df = prepare_frame(df_new, spec["top_origin"], spec["top_dest"], spec["lf_median"])
    out = pd.DataFrame(0.0, index=df.index, columns=spec["columns"], dtype="float32")
    for name, (col, pre) in FACTOR_SPEC.items():
        for i, v in zip(df.index, df[col].astype(str)):
            c = f"{pre}_{v}"
            if c in out.columns:
                out.at[i, c] = 1.0
    for c in ("distance_k", "lf_prev_10", "lf_prev_missing"):
        if c in out.columns:
            out[c] = df[c].astype("float32")
    return out

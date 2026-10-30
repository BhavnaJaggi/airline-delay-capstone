"""Scoring logic for the flight delay risk service.

The same module serves the dashboard (streamlit_app.py) and the programming interface (api.py), so there is one
place where a flight description becomes a prediction. It loads the gradient boosting model and the feature
specification written by notebook 07.

A flight is described by information known before departure only:
carrier, origin, destination, month, day of week, scheduled departure time, distance and (optionally) the previous
month's load factor on the route.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from rq1_features import transform              # noqa: E402
from labels import carrier_name, airport_name    # noqa: E402

MODEL_DIR = HERE / "model"
FACTORS = ["Scheduled departure block", "Month", "Carrier", "Day of week", "Origin airport", "Destination airport",
           "Route distance", "Prior-month load factor"]


class DelayRiskModel:
    def __init__(self, model_dir: Path = MODEL_DIR):
        self.spec = json.load(open(model_dir / "feature_spec.json"))
        self.booster = xgb.Booster()
        self.booster.load_model(str(model_dir / "late_arrival_xgboost.json"))
        lk = model_dir / "route_lookup.csv"
        self.routes = pd.read_csv(lk) if lk.exists() else pd.DataFrame(columns=["origin", "dest", "distance"])
        self.base_rate = float(self.spec["test_prevalence"])
        self.cuts = self.spec.get("risk_cutoffs", {})

    # -- helpers ---------------------------------------------------------------------------------
    @staticmethod
    def time_block(hhmm: int) -> str:
        """Scheduled departure time (e.g. 1745) -> the block used in training (e.g. '1700-1759')."""
        h = int(hhmm) // 100
        if h < 6:                                  # the Bureau groups 00:01 to 05:59 into one block
            return "0001-0559"
        return f"{h:02d}00-{h:02d}59"

    def distance(self, origin: str, dest: str):
        m = self.routes[(self.routes.origin == origin) & (self.routes.dest == dest)]
        return float(m["distance"].iloc[0]) if len(m) else None

    def band(self, p: float) -> str:
        c = self.cuts
        if not c:
            return "unknown"
        if p >= c["high"]:
            return "high"
        if p >= c["elevated"]:
            return "elevated"
        return "typical"

    # -- prediction ------------------------------------------------------------------------------
    def predict(self, carrier, origin, dest, month, day_of_week, dep_time, distance=None, lf_prev=None) -> dict:
        """day_of_week: 1 = Monday ... 7 = Sunday; dep_time: scheduled departure as hhmm (e.g. 1745)."""
        if distance is None:
            distance = self.distance(origin, dest)
        if distance is None:
            raise ValueError(f"distance for {origin}-{dest} is not in the lookup table; pass distance explicitly")
        row = pd.DataFrame([{"carrier": carrier, "origin": origin, "dest": dest, "month": int(month), "day_of_week": int(day_of_week),
                             "dep_time_blk": self.time_block(dep_time), "distance": float(distance),
                             "lf_prev": np.nan if lf_prev is None else float(lf_prev)}])
        X = transform(row, self.spec)
        d = xgb.DMatrix(X.values.astype("float32"), feature_names=list(X.columns))
        p = float(self.booster.predict(d)[0])
        contrib = self.booster.predict(d, pred_contribs=True)[0][:-1]       # log-odds contribution of every column (last = bias)
        by_factor = pd.Series(contrib, index=X.columns).groupby(pd.Series(self.spec["col_to_factor"])).sum()
        by_factor = by_factor.reindex(FACTORS).dropna().sort_values(key=np.abs, ascending=False)
        return {"probability_late": p, "risk_band": self.band(p), "baseline_late_rate": self.base_rate,
                "relative_risk": p / self.base_rate,
                "drivers": [{"factor": f, "log_odds_contribution": float(v), "direction": "raises risk" if v > 0 else "lowers risk"}
                            for f, v in by_factor.items()],
                "inputs": {"carrier": carrier_name(carrier), "origin": airport_name(origin), "destination": airport_name(dest),
                           "month": int(month), "day_of_week": int(day_of_week), "scheduled_departure": int(dep_time),
                           "distance_miles": float(distance), "prior_month_load_factor": lf_prev}}

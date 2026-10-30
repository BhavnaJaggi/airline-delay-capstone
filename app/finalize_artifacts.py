"""Finish the deployment artifacts after notebook 07 has saved the model.

    python app/finalize_artifacts.py

Adds to app/model/:
  * risk cut-offs and the observed late rate in each risk band (computed on the 80,000-flight test set), and
  * route_lookup.csv: the scheduled distance for every origin-destination pair seen in the flight table.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from config import PROCESSED, TOP_AIRPORTS_RQ1, RANDOM_STATE      # noqa: E402
from rq1_features import fit_design                               # noqa: E402
from build_database import connect                                # noqa: E402

MODEL = ROOT / "app" / "model"
spec = json.load(open(MODEL / "feature_spec.json"))
booster = xgb.Booster(); booster.load_model(str(MODEL / "late_arrival_xgboost.json"))

df, X, y, _ = fit_design(pd.read_csv(PROCESSED / "rq1_sample.csv.gz"), TOP_AIRPORTS_RQ1)
assert list(X.columns) == spec["columns"], "feature columns differ from the saved specification"
_, X_te, _, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)
p = booster.predict(xgb.DMatrix(X_te.values.astype("float32"), feature_names=list(X_te.columns)))
print("test AUC of the saved model:", round(roc_auc_score(y_te, p), 4))

elevated, high = float(np.quantile(p, 0.70)), float(np.quantile(p, 0.90))
band = np.where(p >= high, "high", np.where(p >= elevated, "elevated", "typical"))
rates = {b: {"share_of_flights_pct": float((band == b).mean() * 100), "late_rate_pct": float(y_te[band == b].mean() * 100)}
         for b in ("typical", "elevated", "high")}
spec.update({"risk_cutoffs": {"elevated": elevated, "high": high}, "risk_band_rates": rates, "test_auc": float(roc_auc_score(y_te, p))})
json.dump(spec, open(MODEL / "feature_spec.json", "w"), indent=1)
print(json.dumps(spec["risk_cutoffs"]), json.dumps(rates))

con = connect()
lk = con.execute("SELECT CAST(origin AS VARCHAR) AS origin, CAST(dest AS VARCHAR) AS dest, ROUND(MEDIAN(distance)) AS distance, COUNT(*) AS flights "
                 "FROM flight GROUP BY 1, 2 HAVING COUNT(*) >= 20 ORDER BY flights DESC").df()
lk[["origin", "dest", "distance"]].to_csv(MODEL / "route_lookup.csv", index=False)
print("route lookup:", len(lk), "origin-destination pairs")

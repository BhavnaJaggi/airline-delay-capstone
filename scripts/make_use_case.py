"""Score two example flights with the saved model and look up their history in the database (used in the final report).

    python scripts/make_use_case.py

Writes outputs/tables/use_case.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app")); sys.path.insert(0, str(ROOT / "scripts"))
from delay_model import DelayRiskModel      # noqa: E402
from build_database import connect          # noqa: E402

CASES = [
    {"label": "Friday evening in July", "carrier": "AA", "origin": "ORD", "dest": "LGA", "month": 7, "day_of_week": 5, "dep_time": 1845},
    {"label": "Tuesday morning in October", "carrier": "AA", "origin": "ORD", "dest": "LGA", "month": 10, "day_of_week": 2, "dep_time": 745},
]
m = DelayRiskModel()
con = connect()
out = []
for c in CASES:
    r = m.predict(**{k: v for k, v in c.items() if k != "label"})
    blk = m.time_block(c["dep_time"])
    hist = con.execute("""SELECT COUNT(*) AS n, 100.0 * AVG(is_late) AS late FROM flight
                          WHERE operated = 1 AND CAST(carrier AS VARCHAR) = ? AND CAST(origin AS VARCHAR) = ? AND CAST(dest AS VARCHAR) = ?
                          AND CAST(dep_time_blk AS VARCHAR) = ? AND month = ?""", [c["carrier"], c["origin"], c["dest"], blk, c["month"]]).fetchone()
    out.append({**c, "block": blk, "probability_late": r["probability_late"], "risk_band": r["risk_band"], "relative_risk": r["relative_risk"],
                "drivers": r["drivers"][:3], "history_flights": int(hist[0]), "history_late_pct": None if hist[1] is None else float(hist[1])})
path = ROOT / "outputs" / "tables" / "use_case.json"
path.write_text(json.dumps({"cases": out, "baseline": m.base_rate, "cutoffs": m.cuts, "band_rates": m.spec.get("risk_band_rates")}, indent=1))
print(json.dumps(out, indent=1)[:1800])

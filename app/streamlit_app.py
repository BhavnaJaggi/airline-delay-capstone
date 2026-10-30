"""Dashboard for the flight delay risk model (Streamlit).

Run (from the project root):   streamlit run app/streamlit_app.py
A scheduler or dispatcher chooses a flight; the page returns the probability of a late arrival (15 minutes or more),
a risk band, the factors behind the estimate, and how often similar flights were late in the historical data.
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from app.delay_model import DelayRiskModel      # noqa: E402
from labels import CARRIER_NAMES, AIRPORT_NAMES, MONTH_NAMES, DOW_NAMES, carrier_name, airport_name   # noqa: E402

st.set_page_config(page_title="Flight delay risk", layout="wide")


@st.cache_resource
def load_model():
    return DelayRiskModel()


def history(carrier, origin, dest, blk):
    """Optional: historical late rate for the same carrier, route and departure block, read from the database by SQL."""
    try:
        from build_database import connect
        con = connect()
        r = con.execute(
            "SELECT COUNT(*) AS n, 100.0 * AVG(is_late) AS late FROM flight WHERE operated = 1 AND carrier = ? AND origin = ? "
            "AND dest = ? AND dep_time_blk = ?", [carrier, origin, dest, blk]).fetchone()
        con.close()
        return r
    except Exception:
        return None


model = load_model()
spec = model.spec
st.title("Flight delay risk")
st.caption("Probability that a scheduled U.S. domestic flight arrives 15 or more minutes late, from information known before departure. "
           f"Gradient boosting model, test area under the curve {spec['test_auc']:.3f}.")

carriers = sorted(spec["levels"]["Carrier"])
airports = sorted({a for a in spec["top_origin"] + spec["top_dest"]})
c1, c2, c3 = st.columns(3)
with c1:
    carrier = st.selectbox("Airline", carriers, index=carriers.index("WN") if "WN" in carriers else 0, format_func=carrier_name)
    month = st.selectbox("Month", list(range(1, 13)), index=6, format_func=lambda m: MONTH_NAMES[m - 1])
with c2:
    origin = st.selectbox("Origin airport", airports, index=airports.index("DAL") if "DAL" in airports else 0, format_func=airport_name)
    dow = st.selectbox("Day of week", list(range(1, 8)), index=4, format_func=lambda d: DOW_NAMES[d - 1])
with c3:
    dest = st.selectbox("Destination airport", airports, index=airports.index("HOU") if "HOU" in airports else 1, format_func=airport_name)
    dep = st.time_input("Scheduled departure", value=pd.Timestamp("17:45").time(), step=900)
dist = model.distance(origin, dest)
lf = st.number_input("Previous month's load factor on this route (percent, optional; 0 = unknown)", 0.0, 100.0, 0.0, 1.0)
if dist is None:
    dist = st.number_input("Distance in miles (not found in the lookup table)", 50.0, 5000.0, 500.0, 10.0)

if st.button("Estimate delay risk", type="primary"):
    res = model.predict(carrier, origin, dest, month, dow, dep.hour * 100 + dep.minute, distance=dist, lf_prev=lf or None)
    p = res["probability_late"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Probability of a late arrival", f"{p*100:.1f}%", f"{(p/res['baseline_late_rate']-1)*100:+.0f}% vs average flight")
    m2.metric("Risk band", res["risk_band"].capitalize())
    m3.metric("Average flight in the data", f"{res['baseline_late_rate']*100:.1f}%")
    d = pd.DataFrame(res["drivers"]).set_index("factor")["log_odds_contribution"]
    st.subheader("What drives this estimate")
    st.bar_chart(d, horizontal=True)
    st.caption("Positive bars push the estimate up, negative bars push it down (contribution on the log-odds scale).")
    h = history(carrier, origin, dest, model.time_block(dep.hour * 100 + dep.minute))
    if h and h[0]:
        st.info(f"In the 2024 and 2025 data, {h[0]:,} flights with this airline, route and departure block were operated; "
                f"{h[1]:.1f}% arrived 15 or more minutes late.")

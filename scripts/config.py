"""Project-wide settings for the airline delay capstone.

Every notebook imports this module, so the study design lives in ONE place.
Change a value here and re-run the notebooks in order (00 -> 06) to regenerate
every table, figure and number reported in the interim report.
"""
from pathlib import Path

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[1]
RAW_OTP = ROOT / "data" / "raw" / "otp"
RAW_T100 = ROOT / "data" / "raw" / "t100_segment"
RAW_SAMPLE = ROOT / "data" / "raw_sample"
PROCESSED = ROOT / "data" / "processed"
FIG = ROOT / "outputs" / "figures"
TAB = ROOT / "outputs" / "tables"
RESULTS_JSON = ROOT / "outputs" / "results.json"
for _p in (RAW_OTP, RAW_T100, RAW_SAMPLE, PROCESSED, FIG, TAB):
    _p.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- study design
OTP_YEARS = [2024, 2025]   # complete calendar years of flight-level data (RQ1-RQ3); use [2025] if memory is limited
T100_FIRST_YEAR = 2022     # first year of monthly T-100 series (RQ4 needs >= 3 yrs)
T100_LAST_YEAR = 2026      # last year of monthly T-100 series (a partly published year is fine: the last partial month is dropped)
MIN_MONTHS_CARRIER_AIRPORT = 6 * len(OTP_YEARS)   # RQ3: carrier-airport must appear in at least this many months
SERVICE_CLASS = "F"        # T-100 service class F = scheduled passenger service

RANDOM_STATE = 42          # one seed for every random process
RQ1_SAMPLE_N = 400_000     # flights used for RQ1 modelling (minimum required: 9,604)
MIN_FLIGHTS_ROUTE_MONTH = 30   # RQ2: ignore route-months with fewer operated flights
MIN_FLIGHTS_CARRIER_AIRPORT = 120  # RQ3: ignore carrier-airport pairs with fewer flights
TOP_AIRPORTS_RQ1 = 25      # RQ1: top-N origin/destination airports kept; rest -> 'Other'
RQ4_N_ROUTES = 150         # RQ4: busiest routes with complete monthly series
RQ4_TEST_MONTHS = 12       # RQ4: last 12 months held out for forecast evaluation

# ---------------------------------------------------------------- sample-size inputs
ALPHA = 0.05
POWER = 0.80
RQ1_E = 0.01               # +/-1% margin of error
RQ1_P = 0.5                # most conservative proportion
RQ2_R = 0.10               # small correlation
RQ3_P1, RQ3_P2 = 0.015, 0.025   # assumed cancellation rates of two clusters
RQ4_D = 0.30               # small-to-medium paired effect (Cohen's d)

# ---------------------------------------------------------------- colours
# Fixed-order categorical palette (blue, orange, aqua, yellow, magenta, green,
# violet, red) and a one-hue blue ramp for magnitude. Text/ink colours are muted.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
           "#e87ba4", "#008300", "#6250d6", "#e34948"]
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e6e5e1"

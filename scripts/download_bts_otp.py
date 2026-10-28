"""Download the monthly On-Time Performance files from BTS TranStats.

Usage (run on a computer that can reach transtats.bts.gov):

    python scripts/download_bts_otp.py                 # all years in config.OTP_YEARS, 4 files at a time
    python scripts/download_bts_otp.py --year 2025     # one / several years
    python scripts/download_bts_otp.py --workers 6     # more files in parallel

Files are saved to data/raw/otp/. A file is written as *.zip.part and renamed only
when it is complete, so already-finished files are skipped and an interrupted file
is resumed from where it stopped (if the server allows it) when you run the script again.
BTS serves these files slowly (a few MB per minute per connection), which is why
several months are downloaded at the same time.

If BTS changes its file naming, the script prints the failing URL; in that case download
the month through the web form
(https://www.transtats.bts.gov/DL_SelectFields.asp?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr),
tick 'Prezipped File', and save it into data/raw/otp/ - the notebooks accept any file name.
"""
import argparse
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import RAW_OTP, OTP_YEARS

BASE = ("https://transtats.bts.gov/PREZIP/"
        "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip")
_print_lock = threading.Lock()


def say(msg):
    with _print_lock:
        print(msg, flush=True)


def fetch(year, m, attempts=4):
    url = BASE.format(year=year, month=m)
    out = RAW_OTP / f"On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{m}.zip"
    part = out.with_suffix(".zip.part")
    if out.exists() and out.stat().st_size > 1_000_000:
        return f"skip   {out.name} (already downloaded)"
    last = None
    for attempt in range(1, attempts + 1):
        try:
            have = part.stat().st_size if part.exists() else 0
            headers = {"Range": f"bytes={have}-"} if have else {}
            say(f"get    {year}-{m:02d}" + (f" (resuming at {have / 1e6:.1f} MB)" if have else ""))
            with requests.get(url, stream=True, timeout=(30, 120), headers=headers) as r:
                if r.status_code == 416:            # asked for a range beyond the file: it is already complete
                    part.replace(out)
                    return f"saved  {out.name}  ({out.stat().st_size / 1e6:.1f} MB)"
                r.raise_for_status()
                mode = "ab" if (have and r.status_code == 206) else "wb"   # server ignored Range -> start over
                with open(part, mode) as fh:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        fh.write(chunk)
            part.replace(out)
            return f"saved  {out.name}  ({out.stat().st_size / 1e6:.1f} MB)"
        except Exception as exc:  # noqa: BLE001
            last = exc
            say(f"retry  {year}-{m:02d}: {exc} (attempt {attempt}/{attempts})")
            time.sleep(5 * attempt)
    return f"FAILED {url}\n       {last}\n       -> download this month manually (see the top of this file)."


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, nargs="+", default=OTP_YEARS)
    ap.add_argument("--workers", type=int, default=4, help="files downloaded at the same time")
    args = ap.parse_args()
    RAW_OTP.mkdir(parents=True, exist_ok=True)
    jobs = [(y, m) for y in args.year for m in range(1, 13)]
    failed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(fetch, y, m): (y, m) for y, m in jobs}
        for f in as_completed(futs):
            msg = f.result()
            say(msg)
            failed += msg.startswith("FAILED")
    done = len([p for p in RAW_OTP.glob("*.zip") if p.stat().st_size > 1_000_000])
    say(f"\nFinished: {done} complete zip file(s) in {RAW_OTP}; {failed} failed.")

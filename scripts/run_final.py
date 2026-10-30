"""One command that rebuilds everything added for the final report, in the right order.

    python scripts/run_final.py            # about 15-40 minutes on a laptop (notebook 06 and 07 are the slow parts)
    python scripts/run_final.py --skip-notebooks   # only the database, checks and model artifacts

Steps: 1 record the computer used, 2 build the DuckDB database, 3 run notebooks 03, 06 and 07,
4 verify the database against the saved results, 5 save the scoring model files used by the app, 6 score the example flights.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
py = sys.executable


def step(title, args):
    print(f"\n##### {title}", flush=True)
    subprocess.run([py, *args], cwd=ROOT, check=True)


step("1/6 Computer and package versions", ["scripts/print_environment.py"])
step("2/6 Build the DuckDB database", ["scripts/build_database.py"])
if "--skip-notebooks" not in sys.argv:
    step("3/6 Notebooks 03, 06 and 07", ["scripts/run_all.py", "03", "06", "07"])
step("4/6 Verify the database against the pipeline results", ["scripts/db_verify.py"])
step("5/6 Save scoring-model files for the app", ["app/finalize_artifacts.py"])
step("6/6 Score the two example flights used in the report", ["scripts/make_use_case.py"])
print("\nDone. Next: git add -A, commit and push (see RUN_FINAL.md).")

"""Run notebooks 00-07 in order and save the executed copies in place.

    python scripts/run_all.py            # everything
    python scripts/run_all.py 03 04      # only notebooks whose name starts with 03 or 04
"""
import subprocess
import sys
from pathlib import Path

NB = Path(__file__).resolve().parents[1] / "notebooks"

# ---- check the environment first, so a missing package gives a clear message instead of a long traceback
import importlib.util
need = ["numpy", "pandas", "scipy", "sklearn", "statsmodels", "xgboost", "shap", "matplotlib", "pyarrow", "requests", "tensorflow"]
missing = [m for m in need if importlib.util.find_spec(m) is None]
if sys.version_info >= (3, 14) or missing:
    print(f"Python {sys.version.split()[0]} at {sys.executable}")
    if sys.version_info >= (3, 14):
        print("This project needs Python 3.11 or 3.12 (TensorFlow, used for RQ4, does not install on 3.14 yet).")
    if missing:
        print("Missing packages:", ", ".join(missing))
    print("Fix: delete the .venv folder, create it again with python3.12, then run: pip install -r requirements.txt")
    sys.exit(1)
try:
    import xgboost  # noqa: F401  (on a Mac this fails until the OpenMP library is installed)
except Exception as exc:  # noqa: BLE001
    print("XGBoost could not be loaded:", str(exc).strip().splitlines()[0] if str(exc).strip() else exc)
    print("On a Mac run:  brew install libomp   and then run this script again.")
    sys.exit(1)
wanted = sys.argv[1:]

# Register a Jupyter kernel that points at THIS Python (the .venv). Without it, nbconvert can pick up another
# "python3" kernel on the computer (for example the system Python) that does not have the packages installed.
KERNEL = "capstone"
subprocess.run([sys.executable, "-m", "ipykernel", "install", "--user", "--name", KERNEL,
                "--display-name", "Capstone (.venv)"], check=True, stdout=subprocess.DEVNULL)
for nb in sorted(NB.glob("0*.ipynb")):
    if wanted and not any(nb.name.startswith(w) for w in wanted):
        continue
    print(f"\n=== running {nb.name} ===", flush=True)
    subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=7200", f"--ExecutePreprocessor.kernel_name={KERNEL}", str(nb)], check=True, cwd=NB)
print("\nAll done. Figures: outputs/figures | tables: outputs/tables | numbers: outputs/results.json")

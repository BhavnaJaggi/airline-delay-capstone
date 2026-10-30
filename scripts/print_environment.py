"""Record the computer and software used for the analysis (needed for the report's technology statement).

    python scripts/print_environment.py

Writes outputs/tables/environment.json and prints the same facts.
"""
import json
import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "outputs" / "tables"
OUT.mkdir(parents=True, exist_ok=True)


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


info = {"python": sys.version.split()[0], "platform": platform.platform(), "machine": platform.machine(),
        "logical_cores": __import__("os").cpu_count()}
if sys.platform == "darwin":
    info["cpu"] = sh(["sysctl", "-n", "machdep.cpu.brand_string"]) or platform.processor()
    mem = sh(["sysctl", "-n", "hw.memsize"])
    info["memory_gb"] = round(int(mem) / 2**30) if mem.isdigit() else None
    info["physical_cores"] = sh(["sysctl", "-n", "hw.physicalcpu"])
    info["gpu_description"] = sh(["system_profiler", "SPDisplaysDataType"]).split("Chipset Model:")[-1].split("\n")[0].strip() if "Chipset Model" in sh(["system_profiler", "SPDisplaysDataType"]) else ""
else:
    info["cpu"] = platform.processor()
    try:
        import psutil
        info["memory_gb"] = round(psutil.virtual_memory().total / 2**30)
    except Exception:  # noqa: BLE001
        info["memory_gb"] = None
pk = {}
for name in ["numpy", "pandas", "scipy", "scikit-learn", "statsmodels", "xgboost", "shap", "tensorflow", "duckdb", "fastapi", "streamlit", "matplotlib"]:
    try:
        pk[name] = metadata.version(name)
    except metadata.PackageNotFoundError:
        pk[name] = None
info["packages"] = pk
try:
    import tensorflow as tf
    info["tensorflow_gpu_devices"] = [d.name for d in tf.config.list_physical_devices("GPU")]
except Exception:  # noqa: BLE001
    info["tensorflow_gpu_devices"] = None
(OUT / "environment.json").write_text(json.dumps(info, indent=2))
print(json.dumps(info, indent=2))

"""Tiny helper that lets every notebook write its key numbers to ONE json file.

The interim report is built from outputs/results.json, so every number quoted in
the report traces back to a notebook cell.
"""
import json
import numpy as np
from config import RESULTS_JSON


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, float) and np.isnan(o):
        return None
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    return o


def load_results():
    if RESULTS_JSON.exists():
        return json.loads(RESULTS_JSON.read_text())
    return {}


def save_result(key, value):
    """Merge `value` into results.json under `key` (overwrites that key only)."""
    res = load_results()
    res[key] = _clean(value)
    RESULTS_JSON.write_text(json.dumps(res, indent=2, sort_keys=True))
    return res[key]

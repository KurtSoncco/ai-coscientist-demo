"""Undo the disguise: turn a constant fitted on x1, x2, y back into physics.

Only the reveal steps import this. The discovery stages never read key.json.
"""
import json
import math
from pathlib import Path

KEY = Path(__file__).resolve().parent / "key.json"
G_ACCEPTED = 6.674e-11  # m^3 kg^-1 s^-2


def load_key(path=KEY):
    with open(path) as f:
        return json.load(f)


def implied_g(c, key=None):
    """G implied by  y = c * x1^1.5 * x2^-0.5,  given  T = 2*pi*sqrt(a^3 / (G M))."""
    units = (key or load_key())["units"]
    # Seconds per (metre^1.5 * kg^-0.5): undo each unit change in turn.
    k = c * units["y_days"] * 86400 * math.sqrt(units["x2_kg"]) / (units["x1_km"] * 1e3) ** 1.5
    return (2 * math.pi / k) ** 2

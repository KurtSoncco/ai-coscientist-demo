"""Starting hypothesis for OpenEvolve: a deliberately naive law.

OpenEvolve may only rewrite the code between the EVOLVE-BLOCK markers.
"""
import math  # noqa: F401  (available to evolved code)


# EVOLVE-BLOCK-START
def predict_period_days(a_km: float, central_mass_kg: float) -> float:
    """Predict the orbital period (days) from orbit size and central mass.

    Naive guess: period grows linearly with distance and ignores mass.
    """
    return 6.0e-4 * a_km
# EVOLVE-BLOCK-END

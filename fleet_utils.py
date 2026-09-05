# fleet_utils.py
# Helpers shared by the fleet report.

KM_PER_MILE = 1.60934


def km_to_miles(km: float) -> float:
    """Convert a distance in kilometers to miles, for the UK partner report."""
    return km / KM_PER_MILE


def format_number(value: float) -> str:
    """Format a number with one decimal place."""
    return f"{value:.1f}"

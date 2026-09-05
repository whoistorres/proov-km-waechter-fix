# fleet_report.py
# Prints the nightly fleet-health summary for Vossberg Mobility.

from km_wachter import wear_percent, needs_service, SERVICE_INTERVAL_KM
from config_loader import load_settings, get_setting
from log_util import log, flush_log
import fleet_utils


def car_wear(car: dict) -> float | None:
    """Return a car's wear percent, or None if it has no last-service reading."""
    last = car.get("last_service_km")
    if last is None:
        return None
    return wear_percent(car["odometer"] - last, SERVICE_INTERVAL_KM)


def fleet_summary(fleet: list[dict]) -> dict:
    """Summarize the fleet: car count, cars due for service, and average wear.

    Cars with no last-service reading are still counted and checked for
    due-status, but excluded from the average-wear total since their wear
    cannot be determined.
    """
    total = 0.0
    readable = 0
    due = 0
    for car in fleet:
        wear = car_wear(car)
        if wear is not None:
            total += wear
            readable += 1
        if needs_service(car):
            due += 1
    average = total / readable if readable else 0.0
    return {"count": len(fleet), "due": due, "average_wear": average}


def print_report(fleet: list[dict]) -> None:
    """Print the nightly fleet report and flush it to the log file."""
    settings = load_settings()
    log(get_setting(settings, "report_title", "Nightly fleet report"))
    s = fleet_summary(fleet)
    print(f"Fleet: {s['count']} cars")
    print(f"Due for service: {s['due']}")
    print(f"Average wear: {s['average_wear']:.1f}%")
    total_km = sum(car["odometer"] for car in fleet)
    # The partner garage in England wants the distance in miles (since 2015).
    print(f"Fleet distance: {fleet_utils.format_number(fleet_utils.km_to_miles(total_km))} miles")
    flush_log(get_setting(settings, "log_file", "km_wachter.log"))

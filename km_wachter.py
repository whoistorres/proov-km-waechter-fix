# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return the precise percentage of a service interval used up."""
    return (km_since_service / interval) * 100


def needs_service(car: dict) -> bool:
    """Return True if a car has used up WARN_AT_PERCENT or more of its interval.

    A car with no last_service_km reading has unknown wear, so it is never flagged.
    """
    last = car.get("last_service_km")
    if last is None:
        return False
    km_since = car["odometer"] - last
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    return pct >= WARN_AT_PERCENT


def check_fleet(fleet: list[dict]) -> list[str]:
    """Return the ids of the cars in the fleet that are due for service."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged

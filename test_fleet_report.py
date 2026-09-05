# test_fleet_report.py
from fleet_report import fleet_summary

SAMPLE = [
    {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    {"id": "VOS-2210", "odometer": 48400, "last_service_km": 45000},
]


def test_summary_counts_due_cars():
    # Only VOS-4471 is nearly worn, so exactly one car is due.
    assert fleet_summary(SAMPLE)["due"] == 1


def test_summary_handles_missing_reading_without_crashing():
    # VOS-7788 has no last_service_km reading, like in fleet_sample.json. This used to crash.
    fleet = SAMPLE + [{"id": "VOS-7788", "odometer": 92000}]
    result = fleet_summary(fleet)
    assert result["count"] == 3
    assert result["due"] == 1
    assert "average_wear" in result


def test_average_wear_is_precise():
    # Two cars at 99.3% and 20.0% worn should average to about 59.67%, not a floored integer.
    fleet = [
        {"id": "A", "odometer": 14900, "last_service_km": 0},
        {"id": "B", "odometer": 3000, "last_service_km": 0},
    ]
    average = fleet_summary(fleet)["average_wear"]
    assert abs(average - 59.67) < 0.1

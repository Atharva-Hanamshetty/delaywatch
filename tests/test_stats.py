from datetime import datetime, timedelta

from app.services.stats import remove_outliers, weighted_average

NOW = datetime(2026, 1, 1, 12, 0, 0)


def post_report(client, delay, train="12604"):
    return client.post(
        "/reports",
        json={"train_number": train, "station_code": "MAS", "delay_minutes": delay},
    )


def test_outlier_is_removed():
    items = [(10, NOW), (12, NOW), (300, NOW)]
    kept = [delay for delay, _ in remove_outliers(items)]
    assert kept == [10, 12]


def test_recent_reports_weigh_more():
    items = [(10, NOW - timedelta(minutes=120)), (30, NOW)]
    assert weighted_average(items, NOW) > 20


def test_live_delay_with_no_reports(client):
    data = client.get("/trains/12604/live").json()
    assert data["live_delay_minutes"] is None
    assert data["based_on_reports"] == 0


def test_live_delay_ignores_outlier(client):
    for delay in (10, 12, 14, 300):
        post_report(client, delay)
    data = client.get("/trains/12604/live").json()
    assert data["based_on_reports"] == 3
    assert 11 <= data["live_delay_minutes"] <= 13


def test_reliability_score(client):
    for delay in (0, 3, 10, 20):
        post_report(client, delay)
    data = client.get("/trains/12604/reliability").json()
    assert data["reliability_score"] == 50.0
    assert data["total_reports"] == 4


def test_reliability_with_no_reports(client):
    data = client.get("/trains/99999/reliability").json()
    assert data["reliability_score"] is None
    assert data["total_reports"] == 0
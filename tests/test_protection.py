from app.services.ratelimit import report_limiter


def post_report(client, delay, train="12604"):
    return client.post(
        "/reports",
        json={"train_number": train, "station_code": "MAS", "delay_minutes": delay},
    )


def test_reliability_ignores_outlier(client):
    for delay in (10, 12, 14, 300):
        post_report(client, delay)
    data = client.get("/trains/12604/reliability").json()
    assert data["total_reports"] == 3
    assert data["average_delay_minutes"] == 12.0


def test_rate_limit_blocks_spam(client):
    for _ in range(report_limiter.max_requests):
        assert post_report(client, 10).status_code == 201
    assert post_report(client, 10).status_code == 429


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "DelayWatch" in response.text
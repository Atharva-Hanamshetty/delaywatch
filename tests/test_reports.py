from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_report_uppercases_station():
    response = client.post(
        "/reports",
        json={"train_number": "12604", "station_code": "mas", "delay_minutes": 10},
    )
    assert response.status_code == 201
    assert response.json()["station_code"] == "MAS"


def test_rejects_non_numeric_train_number():
    response = client.post(
        "/reports",
        json={"train_number": "abcde", "station_code": "MAS", "delay_minutes": 10},
    )
    assert response.status_code == 422


def test_rejects_negative_delay():
    response = client.post(
        "/reports",
        json={"train_number": "12604", "station_code": "MAS", "delay_minutes": -5},
    )
    assert response.status_code == 422
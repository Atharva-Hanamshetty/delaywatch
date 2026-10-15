from app.seed import seed_demo_data


def test_seed_fills_empty_db_only_once(db_session):
    assert seed_demo_data(db_session) > 0
    assert seed_demo_data(db_session) == 0


def test_seeded_train_has_live_delay(client, db_session):
    seed_demo_data(db_session)
    data = client.get("/trains/12604/live").json()
    assert data["live_delay_minutes"] is not None
    assert data["based_on_reports"] >= 3
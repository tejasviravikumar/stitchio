def test_root(client):
    assert client.get("/").json()["docs"] == "/docs"


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200 and response.json()["status"] == "ok"


def test_ready_checks_database(client):
    assert client.get("/api/health/ready").json()["database"] == "ok"

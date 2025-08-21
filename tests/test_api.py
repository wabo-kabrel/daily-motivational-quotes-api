import pytest
from motivation_api.app import app, db
from motivation_api.models import Quote


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # in-memory DB
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed test data
            db.session.add_all([
                Quote(text="Test Quote 1", author="Author 1"),
                Quote(text="Test Quote 2", author="Author 2"),
            ])
            db.session.commit()
        yield client
        # Cleanup
        with app.app_context():
            db.drop_all()

# ------------------------
# Test health endpoint
# ------------------------
def test_health(client):
    rv = client.get("/health")
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert json_data["success"] == True
    assert json_data["data"]["status"] == "ok"

# ------------------------
# Test random quote
# ------------------------
def test_random_quote(client):
    rv = client.get("/api/v1/quote")
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert json_data["success"] == True
    assert "text" in json_data["data"]
    assert "author" in json_data["data"]

# ------------------------
# Test QOTD deterministic
# ------------------------
def test_qotd(client):
    rv1 = client.get("/api/v1/qotd")
    rv2 = client.get("/api/v1/qotd")
    assert rv1.status_code == 200
    assert rv2.status_code == 200
    # QOTD should be deterministic
    assert rv1.get_json()["data"]["id"] == rv2.get_json()["data"]["id"]

# ------------------------
# Test list quotes with pagination
# ------------------------
def test_list_quotes(client):
    rv = client.get("/api/v1/quotes?limit=1&offset=0")
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert len(json_data["data"]) == 1

# ------------------------
# Test error handling
# ------------------------
def test_not_found(client):
    rv = client.get("/api/v1/nonexistent")
    json_data = rv.get_json()
    assert rv.status_code == 404
    assert json_data["success"] == False

# ------------------------
# Admin Endpoints
# ------------------------
def test_create_quote(client):
    rv = client.post("/api/v1/quotes",
                     json={"text":"New","author":"Tester"},
                     headers={"x-api-key":"changeme123"})
    assert rv.status_code == 201
    assert rv.get_json()["success"] == True


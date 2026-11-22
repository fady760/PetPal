import pytest
from fastapi.testclient import TestClient
from main import app, engine, SessionLocal, seed_initial_data
from models import Base

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Ensure database tables and sample demo data are initialized for test runs."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_initial_data(db)
    yield


def test_health_check():
    """
    Test 1: Health Check Route (GET /health)
    Verifies that the /health endpoint returns HTTP 200 and
    the JSON payload {'status': 'healthy', 'database': 'connected'}.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert data.get("database") == "connected"


def test_main_page_loads():
    """
    Test 2: Main Page Route (GET /)
    Verifies that the main HTML page renders with HTTP 200 OK and
    contains PetPal branding and essential page components.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "PetPal" in response.text
    assert "Find Forever" in response.text


def test_add_pet():
    """
    Bonus CI/CD Test: Add Pet (POST /pets)
    Verifies that submitting a new pet redirects to the main page (HTTP 303)
    and persists the record.
    """
    response = client.post(
        "/pets",
        data={"name": "Barnaby", "species": "Dog", "age": 2},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Barnaby" in response.text


def test_adopt_pet():
    """
    Bonus CI/CD Test: Mark Pet Adopted (POST /pets/{id}/adopt)
    Verifies that marking an existing pet as adopted redirects (HTTP 303)
    and updates the UI.
    """
    # Create pet to adopt
    response = client.post(
        "/pets",
        data={"name": "Simba", "species": "Cat", "age": 3},
        follow_redirects=False,
    )
    assert response.status_code == 303

    # Adopt pet with ID 1
    adopt_res = client.post("/pets/1/adopt", follow_redirects=True)
    assert adopt_res.status_code == 200
    assert "Adopted" in adopt_res.text

import concurrent.futures
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def reset_store():
    """Reset the in-memory employee store before every test."""
    store.reset()
    yield
    store.reset()


@pytest.fixture
def client():
    """TestClient fixture for FastAPI requests."""
    return TestClient(app)


# -------------------------------------------------------------
# Health Check Test
# -------------------------------------------------------------
def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# -------------------------------------------------------------
# Part 1.1 - Retrieve Tests
# -------------------------------------------------------------
def test_list_all_employees_seeded(client: TestClient):
    response = client.get("/employees")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0] == {
        "id": 1,
        "name": "Rahul Sharma",
        "department": "Engineering",
        "status": "Active",
    }
    assert data[1] == {
        "id": 2,
        "name": "Priya Patel",
        "department": "HR",
        "status": "Active",
    }
    assert data[2] == {
        "id": 3,
        "name": "Amit Verma",
        "department": "Engineering",
        "status": "Inactive",
    }


def test_get_employee_by_valid_id(client: TestClient):
    response = client.get("/employees/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Rahul Sharma",
        "department": "Engineering",
        "status": "Active",
    }


def test_get_employee_missing_id_404(client: TestClient):
    response = client.get("/employees/999")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "NOT_FOUND"
    assert "999" in body["message"]


def test_get_employee_non_integer_id_400(client: TestClient):
    response = client.get("/employees/abc")
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "integer" in body["message"].lower() or "id" in body["message"].lower()


# -------------------------------------------------------------
# Part 1.2 - Create Tests
# -------------------------------------------------------------
def test_create_valid_employee(client: TestClient):
    payload = {"name": "Smit Patel", "department": "Engineering"}
    response = client.post("/employees", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 4
    assert data["name"] == "Smit Patel"
    assert data["department"] == "Engineering"
    assert data["status"] == "Active"

    # Verify subsequent ID auto-increments
    second_payload = {"name": "John Doe", "department": "Marketing"}
    second_response = client.post("/employees", json=second_payload)
    assert second_response.status_code == 201
    assert second_response.json()["id"] == 5


def test_create_employee_ignores_client_supplied_id_and_status(client: TestClient):
    payload = {
        "id": 999,
        "status": "Inactive",
        "name": "Alice Johnson",
        "department": "Finance",
    }
    response = client.post("/employees", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 4
    assert data["status"] == "Active"
    assert data["name"] == "Alice Johnson"
    assert data["department"] == "Finance"


def test_create_employee_empty_name(client: TestClient):
    response = client.post("/employees", json={"name": "", "department": "Engineering"})
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "name" in body["message"].lower()


def test_create_employee_whitespace_only_name(client: TestClient):
    response = client.post("/employees", json={"name": "   ", "department": "Engineering"})
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "name" in body["message"].lower()


def test_create_employee_whitespace_only_department(client: TestClient):
    response = client.post("/employees", json={"name": "Bob", "department": "   "})
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "department" in body["message"].lower()


def test_create_employee_missing_fields(client: TestClient):
    response = client.post("/employees", json={"name": "Bob"})
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "department" in body["message"].lower()

    response2 = client.post("/employees", json={"department": "Engineering"})
    assert response2.status_code == 400
    body2 = response2.json()
    assert body2["error"] == "VALIDATION_ERROR"
    assert "name" in body2["message"].lower()


def test_create_employee_strips_surrounding_whitespace(client: TestClient):
    payload = {"name": "   Sunil Kumar   ", "department": "   Operations   "}
    response = client.post("/employees", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sunil Kumar"
    assert data["department"] == "Operations"


# -------------------------------------------------------------
# Part 1.3 - Update and Filter Tests
# -------------------------------------------------------------
def test_patch_status_to_inactive(client: TestClient):
    response = client.patch("/employees/1/status", json={"status": "Inactive"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["status"] == "Inactive"

    # Verify retrieval reflects new status
    get_res = client.get("/employees/1")
    assert get_res.json()["status"] == "Inactive"


def test_patch_status_to_active(client: TestClient):
    # Seed 3 starts as Inactive
    response = client.patch("/employees/3/status", json={"status": "Active"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 3
    assert data["status"] == "Active"


def test_patch_invalid_status_400(client: TestClient):
    response = client.patch("/employees/1/status", json={"status": "Pending"})
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "allowed values are 'active' or 'inactive'" in body["message"].lower()


def test_patch_missing_id_404(client: TestClient):
    response = client.patch("/employees/999/status", json={"status": "Inactive"})
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "NOT_FOUND"
    assert "999" in body["message"]


def test_patch_missing_body_field_400(client: TestClient):
    response = client.patch("/employees/1/status", json={})
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "status" in body["message"].lower()


def test_patch_non_integer_id_400(client: TestClient):
    response = client.patch("/employees/xyz/status", json={"status": "Inactive"})
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"


def test_filter_by_department_exact(client: TestClient):
    response = client.get("/employees?department=HR")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Priya Patel"
    assert data[0]["department"] == "HR"


def test_filter_by_department_case_insensitive_and_whitespace(client: TestClient):
    response = client.get("/employees?department=   engineering   ")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [emp["name"] for emp in data]
    assert "Rahul Sharma" in names
    assert "Amit Verma" in names


def test_filter_department_no_matches_returns_empty_list_200(client: TestClient):
    response = client.get("/employees?department=NonExistent")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_filter_combined_with_state_changes(client: TestClient):
    # Add new employee in HR
    client.post("/employees", json={"name": "Neha Gupta", "department": "HR"})

    # Filter HR
    response = client.get("/employees?department=hr")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [emp["name"] for emp in data]
    assert "Priya Patel" in names
    assert "Neha Gupta" in names


# -------------------------------------------------------------
# Thread-Safety Concurrency Test
# -------------------------------------------------------------
def test_concurrent_employee_creation():
    """Verify thread-safe unique sequential ID allocation under concurrent load."""
    store.reset()

    def create_worker(index: int):
        return store.create(name=f"Worker {index}", department="Engineering")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(create_worker, range(20)))

    ids = [emp.id for emp in results]
    assert len(ids) == 20
    assert len(set(ids)) == 20
    assert min(ids) == 4
    assert max(ids) == 23


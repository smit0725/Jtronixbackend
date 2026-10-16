# JTRONIX Employee Management REST API

A production-grade, thread-safe, in-memory REST API built in Python with **FastAPI** and **Pydantic v2** for the JTRONIX Backend Internship Assessment.

---

## Completion Status

- [x] **Part 1.1 - Retrieve**: Seeded data startup, `GET /employees` (list all), `GET /employees/{id}`, standardized `404 NOT_FOUND` error handling.
- [x] **Part 1.2 - Create**: `POST /employees` with input validation, automatic ID generation (starting at 4), default status `Active`, client-supplied `id` and `status` ignored, empty/whitespace strings rejected with `400 VALIDATION_ERROR`.
- [x] **Part 1.3 - Update and Filter**: `PATCH /employees/{id}/status` with strict enum validation (`Active` | `Inactive`), case-insensitive `GET /employees?department=...` filtering with trimmed whitespace and empty list on no matches.
- [x] **Automated Tests**: 23 automated unit and integration tests covering positive flows, concurrency, and all error conditions.
- [x] **Postman Collection**: Exported Postman Collection v2.1 with environment variables, tests, and saved examples.

> **Note**: As requested by the assessment specification, all records are kept strictly in-memory without a persistent database. State is reset to initial seed values whenever the application restarts.

---

## Tech Stack

- **Python 3.11+** (Tested on Python 3.13)
- **FastAPI**: Modern, high-performance web framework with automatic OpenAPI documentation.
- **Pydantic v2**: Strict schema validation and serialization.
- **Uvicorn**: Lightning-fast ASGI web server implementation.
- **pytest & HTTPX**: Automated integration and unit testing with `TestClient`.

---

## Project Structure

```text
c:\Jtronix_assesment_backend\
├── app/
│   ├── __init__.py          # App package initializer
│   ├── main.py              # Application factory, middleware & exception handlers
│   ├── models.py            # Pydantic schemas, enums & request/response validators
│   ├── store.py             # Thread-safe in-memory store protected by threading.Lock
│   ├── routes.py            # APIRouter definitions for /employees endpoints
│   └── errors.py            # Standardized error definitions & exception handlers
├── tests/
│   ├── __init__.py          # Test suite package initializer
│   └── test_employees.py    # 23 automated pytest test cases
├── postman/
│   └── Employee_API.postman_collection.json # Ready-to-import Postman v2.1 collection
├── requirements.txt         # Pinned minimum dependencies
├── README.md                # Project documentation and guide
└── .gitignore               # Ignored files (venv, caches, etc.)
```

---

## Setup & Installation

### 1. Clone & Navigate
```bash
git clone https://github.com/smit0725/Jtronixbackend.git
cd Jtronixbackend
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell script execution is restricted, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` or activate using `.\venv\Scripts\activate.bat`)*

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the development server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The server will start listening at:
- **Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

---

## API Endpoints Reference

| Method | Endpoint | Description | Success Code | Error Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service health status check | `200 OK` | - |
| `GET` | `/employees` | Retrieve all employees, or filter by `?department=` | `200 OK` | `400 VALIDATION_ERROR` |
| `GET` | `/employees/{id}` | Retrieve a single employee by integer ID | `200 OK` | `400 VALIDATION_ERROR`, `404 NOT_FOUND` |
| `POST` | `/employees` | Create a new employee (`Active` status, auto ID) | `201 Created` | `400 VALIDATION_ERROR` |
| `PATCH`| `/employees/{id}/status` | Update employee status (`Active` or `Inactive`) | `200 OK` | `400 VALIDATION_ERROR`, `404 NOT_FOUND` |

---

## Error Response Format

All error responses across the API strictly follow a uniform JSON structure:

```json
{
  "error": "<ERROR_CODE>",
  "message": "<Human-readable explanation>"
}
```

### Standard Error Codes
- `VALIDATION_ERROR` (HTTP 400): Raised on invalid path parameters (e.g. non-integer ID), empty/whitespace fields, invalid JSON, or invalid enum values.
- `NOT_FOUND` (HTTP 404): Raised when an employee with the specified ID does not exist.
- `METHOD_NOT_ALLOWED` (HTTP 405): Raised when invoking an unsupported HTTP verb.
- `INTERNAL_SERVER_ERROR` (HTTP 500): Generic fallback handler that logs errors without leaking internal stack traces.

---

## Seed Data

On application startup, the store initializes with the three required records:

| ID | Name | Department | Status |
| :---: | :--- | :--- | :--- |
| 1 | Rahul Sharma | Engineering | Active |
| 2 | Priya Patel | HR | Active |
| 3 | Amit Verma | Engineering | Inactive |

New employees created via `POST /employees` start with `id: 4` and increment sequentially (`5`, `6`, etc.).

---

## cURL Examples & Sample Responses

### 1. Health Check
```bash
curl -X GET http://127.0.0.1:8000/health
```
**Response (200 OK):**
```json
{
  "status": "ok"
}
```

### 2. List All Employees
```bash
curl -X GET http://127.0.0.1:8000/employees
```
**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Rahul Sharma",
    "department": "Engineering",
    "status": "Active"
  },
  {
    "id": 2,
    "name": "Priya Patel",
    "department": "HR",
    "status": "Active"
  },
  {
    "id": 3,
    "name": "Amit Verma",
    "department": "Engineering",
    "status": "Inactive"
  }
]
```

### 3. Filter Employees by Department (Case-Insensitive)
```bash
curl -X GET "http://127.0.0.1:8000/employees?department=engineering"
```
**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Rahul Sharma",
    "department": "Engineering",
    "status": "Active"
  },
  {
    "id": 3,
    "name": "Amit Verma",
    "department": "Engineering",
    "status": "Inactive"
  }
]
```

### 4. Filter with No Matches
```bash
curl -X GET "http://127.0.0.1:8000/employees?department=Finance"
```
**Response (200 OK):**
```json
[]
```

### 5. Get Employee by Valid ID
```bash
curl -X GET http://127.0.0.1:8000/employees/1
```
**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Rahul Sharma",
  "department": "Engineering",
  "status": "Active"
}
```

### 6. Get Missing Employee (404 Not Found)
```bash
curl -X GET http://127.0.0.1:8000/employees/999
```
**Response (404 Not Found):**
```json
{
  "error": "NOT_FOUND",
  "message": "Employee with ID 999 not found"
}
```

### 7. Get Employee with Non-Integer ID (400 Bad Request)
```bash
curl -X GET http://127.0.0.1:8000/employees/abc
```
**Response (400 Bad Request):**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "id: Input should be a valid integer, unable to parse string as an integer"
}
```

### 8. Create a New Employee
```bash
curl -X POST http://127.0.0.1:8000/employees \
  -H "Content-Type: application/json" \
  -d '{"name": "Neha Gupta", "department": "Marketing"}'
```
**Response (201 Created):**
```json
{
  "id": 4,
  "name": "Neha Gupta",
  "department": "Marketing",
  "status": "Active"
}
```

### 9. Create Employee with Client-Supplied ID/Status (Ignored)
```bash
curl -X POST http://127.0.0.1:8000/employees \
  -H "Content-Type: application/json" \
  -d '{"name": "Dev User", "department": "Security", "id": 999, "status": "Inactive"}'
```
**Response (201 Created):**
```json
{
  "id": 5,
  "name": "Dev User",
  "department": "Security",
  "status": "Active"
}
```

### 10. Create Employee Validation Error (Empty Name)
```bash
curl -X POST http://127.0.0.1:8000/employees \
  -H "Content-Type: application/json" \
  -d '{"name": "   ", "department": "Sales"}'
```
**Response (400 Bad Request):**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "name: Name cannot be empty or whitespace-only"
}
```

### 11. Update Employee Status
```bash
curl -X PATCH http://127.0.0.1:8000/employees/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "Inactive"}'
```
**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Rahul Sharma",
  "department": "Engineering",
  "status": "Inactive"
}
```

### 12. Update Status with Invalid Value
```bash
curl -X PATCH http://127.0.0.1:8000/employees/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "OnLeave"}'
```
**Response (400 Bad Request):**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "status: Invalid status value. Allowed values are 'Active' or 'Inactive'"
}
```

---

## Running Automated Tests

Run the test suite using `pytest`:

```bash
pytest -v
```

All 23 tests will execute against `TestClient`, checking:
- Health check
- Retrieval and 404/400 validation
- Creation, whitespace trimming, empty string rejection, and ID incrementation
- Status updates (`Active` $\leftrightarrow$ `Inactive`) and enum rejection
- Department query filters (case-insensitivity, whitespace, no matches)
- Concurrent thread-safety and atomic ID generation

---

## Postman Collection Usage

1. Open Postman.
2. Click **Import** and select `postman/Employee_API.postman_collection.json`.
3. The collection is pre-configured with a `{{baseUrl}}` variable defaulting to `http://127.0.0.1:8000`.
4. Run individual requests or use the **Collection Runner** to execute all requests and assertions.

---

## Architectural & Design Decisions

1. **FastAPI & Pydantic v2**:
   - Provides out-of-the-box OpenAPI (`/docs`) interactive documentation.
   - Pydantic v2 field validators perform high-performance sanitization and whitespace trimming.
2. **Unified Error Handler (FastAPI 422 $\to$ 400)**:
   - FastAPI defaults to returning HTTP 422 for schema validation errors. By registering a custom handler for `RequestValidationError`, all validation errors (malformed JSON, type mismatches like `/employees/abc`, empty fields, invalid enums) consistently return `400 Bad Request` with an identical `{ "error": "VALIDATION_ERROR", "message": "..." }` payload.
3. **Thread Safety with `threading.Lock`**:
   - In-memory data structures are vulnerable to race conditions under asynchronous or multi-threaded server environments. All reads, updates, and sequential ID increments are protected by a mutex lock, ensuring zero ID collision or data corruption.
4. **Separation of Concerns**:
   - `store.py` encapsulates pure repository business logic and concurrency.
   - `models.py` defines schemas and data integrity constraints.
   - `routes.py` handles HTTP endpoints, parameters, and response status codes.
   - `errors.py` standardizes API exception handling.
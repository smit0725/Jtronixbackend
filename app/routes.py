from typing import Optional
from fastapi import APIRouter, Path, Query, status
from app.models import Employee, EmployeeCreate, EmployeeStatusUpdate, ErrorResponse
from app.store import store

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get(
    "",
    response_model=list[Employee],
    status_code=status.HTTP_200_OK,
    summary="List all employees",
    description="Retrieve all employees or filter them by department (case-insensitive).",
    responses={
        200: {
            "description": "List of employees matching query or all employees if no filter is applied.",
            "model": list[Employee],
        }
    },
)
def list_employees(
    department: Optional[str] = Query(
        default=None,
        description="Filter employees by department name (case-insensitive)",
    )
) -> list[Employee]:
    """Retrieve employees from the in-memory store."""
    return store.get_all(department=department)


@router.get(
    "/{id}",
    response_model=Employee,
    status_code=status.HTTP_200_OK,
    summary="Get employee by ID",
    description="Retrieve a single employee by their unique integer ID.",
    responses={
        200: {"description": "Employee found.", "model": Employee},
        400: {"description": "Invalid employee ID parameter.", "model": ErrorResponse},
        404: {"description": "Employee not found.", "model": ErrorResponse},
    },
)
def get_employee(
    id: int = Path(..., description="The unique integer ID of the employee", ge=1)
) -> Employee:
    """Retrieve a single employee by ID."""
    return store.get_by_id(id)


@router.post(
    "",
    response_model=Employee,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
    description="Create an employee with automatic ID generation and status defaulted to 'Active'.",
    responses={
        201: {"description": "Employee successfully created.", "model": Employee},
        400: {"description": "Invalid input data.", "model": ErrorResponse},
    },
)
def create_employee(payload: EmployeeCreate) -> Employee:
    """Create a new employee record."""
    return store.create(name=payload.name, department=payload.department)


@router.patch(
    "/{id}/status",
    response_model=Employee,
    status_code=status.HTTP_200_OK,
    summary="Update employee status",
    description="Update the status of an existing employee to 'Active' or 'Inactive'.",
    responses={
        200: {"description": "Employee status updated successfully.", "model": Employee},
        400: {"description": "Invalid status value or invalid ID.", "model": ErrorResponse},
        404: {"description": "Employee not found.", "model": ErrorResponse},
    },
)
def update_employee_status(
    payload: EmployeeStatusUpdate,
    id: int = Path(..., description="The unique integer ID of the employee", ge=1),
) -> Employee:
    """Update employee status."""
    return store.update_status(id, payload.status)

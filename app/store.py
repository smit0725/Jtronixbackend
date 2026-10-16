import threading
from typing import Optional
from app.errors import NotFoundError
from app.models import Employee, StatusEnum

INITIAL_SEEDS: list[dict] = [
    {"id": 1, "name": "Rahul Sharma", "department": "Engineering", "status": StatusEnum.ACTIVE},
    {"id": 2, "name": "Priya Patel", "department": "HR", "status": StatusEnum.ACTIVE},
    {"id": 3, "name": "Amit Verma", "department": "Engineering", "status": StatusEnum.INACTIVE},
]


class EmployeeStore:
    """Thread-safe in-memory repository for employee records."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._employees: dict[int, Employee] = {}
        self._next_id: int = 4
        self.reset()

    def reset(self) -> None:
        """Reset repository to the initial seed state and reset the ID counter to 4."""
        with self._lock:
            self._employees.clear()
            for seed in INITIAL_SEEDS:
                self._employees[seed["id"]] = Employee(**seed)
            self._next_id = 4

    def get_all(self, department: Optional[str] = None) -> list[Employee]:
        """Retrieve all employees, optionally filtered by department (case-insensitive)."""
        with self._lock:
            employees = list(self._employees.values())

        if department is not None:
            cleaned_dep = department.strip().lower()
            employees = [emp for emp in employees if emp.department.strip().lower() == cleaned_dep]

        return employees

    def get_by_id(self, employee_id: int) -> Employee:
        """Retrieve an employee by ID. Raises NotFoundError if absent."""
        with self._lock:
            emp = self._employees.get(employee_id)

        if emp is None:
            raise NotFoundError(f"Employee with ID {employee_id} not found")
        return emp

    def create(self, name: str, department: str) -> Employee:
        """Create a new employee with automatically generated ID and status Active."""
        with self._lock:
            new_id = self._next_id
            self._next_id += 1
            employee = Employee(
                id=new_id,
                name=name.strip(),
                department=department.strip(),
                status=StatusEnum.ACTIVE,
            )
            self._employees[new_id] = employee
            return employee

    def update_status(self, employee_id: int, status: StatusEnum) -> Employee:
        """Update the status of an existing employee. Raises NotFoundError if absent."""
        with self._lock:
            emp = self._employees.get(employee_id)
            if emp is None:
                raise NotFoundError(f"Employee with ID {employee_id} not found")

            updated = emp.model_copy(update={"status": status})
            self._employees[employee_id] = updated
            return updated


# Global singleton instance
store = EmployeeStore()


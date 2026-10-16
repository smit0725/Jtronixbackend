from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, field_validator


class StatusEnum(str, Enum):
    """Allowed employee status values."""

    ACTIVE = "Active"
    INACTIVE = "Inactive"


class Employee(BaseModel):
    """Employee data model representing an individual employee record."""

    id: int
    name: str
    department: str
    status: StatusEnum


class EmployeeCreate(BaseModel):
    """Request schema for creating a new employee."""

    model_config = ConfigDict(extra="ignore")

    name: str
    department: str

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        stripped = value.strip()
        if not stripped:
            raise ValueError("Name cannot be empty or whitespace-only")
        return stripped

    @field_validator("department", mode="before")
    @classmethod
    def validate_department(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("Department must be a string")
        stripped = value.strip()
        if not stripped:
            raise ValueError("Department cannot be empty or whitespace-only")
        return stripped


class EmployeeStatusUpdate(BaseModel):
    """Request schema for updating an employee's status."""

    model_config = ConfigDict(extra="ignore")

    status: StatusEnum

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: Any) -> Any:
        if not isinstance(value, str) or value not in (StatusEnum.ACTIVE.value, StatusEnum.INACTIVE.value):
            raise ValueError("Invalid status value. Allowed values are 'Active' or 'Inactive'")
        return value


class ErrorResponse(BaseModel):
    """Standardized error response body."""

    error: str
    message: str


class HealthResponse(BaseModel):
    """Health check response body."""

    status: str = "ok"


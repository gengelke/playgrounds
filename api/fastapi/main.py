from __future__ import annotations

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import os
import sqlite3
from pathlib import Path

import strawberry
from strawberry.fastapi import GraphQLRouter


app = FastAPI()

# Prefer mounted Docker path if available; otherwise use repo-local sqlite path.
default_db_path = Path("/data/company.sqlite") if Path("/data").exists() else Path(__file__).resolve().parent.parent / "company.sqlite"
DATABASE = os.getenv("DATABASE_PATH", str(default_db_path))


# =====================================================
# DATABASE LAYER (CENTRALIZED)
# =====================================================

def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INTEGER PRIMARY KEY,
        name TEXT,
        surname TEXT,
        description TEXT
    )
    """)

    conn.commit()
    conn.close()


def seed_initial_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM employees")
    result = cursor.fetchone()

    if result["count"] == 0:
        cursor.execute("""
        INSERT INTO employees (employee_id, name, surname, description)
        VALUES (?, ?, ?, ?)
        """, (1, "Flash", "Gordon", "Superhero"))
        conn.commit()

    conn.close()


def get_employees_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()

    conn.close()
    return [dict(row) for row in rows]


def get_employee_db(employee_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM employees WHERE employee_id = ?",
        (employee_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)

    return None


def get_employee_by_surname_db(surname: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM employees WHERE surname = ?",
        (surname,)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)

    return None


def add_employee_db(employee_id, name, surname, description):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO employees (employee_id, name, surname, description)
    VALUES (?, ?, ?, ?)
    """, (employee_id, name, surname, description))

    conn.commit()
    conn.close()


def update_employee_db(employee_id, name, surname, description):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE employees
    SET name = ?, surname = ?, description = ?
    WHERE employee_id = ?
    """, (name, surname, description, employee_id))

    conn.commit()
    conn.close()


def delete_employee_db(employee_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM employees WHERE employee_id = ?",
                   (employee_id,))

    conn.commit()
    conn.close()


# =====================================================
# STARTUP
# =====================================================

@app.on_event("startup")
def startup_event():
    create_table()
    seed_initial_data()


# Optional: Export schema via curl
# GET /schema.graphql
# =====================================================
# Will be available after schema definition below


# =====================================================
# REST API
# =====================================================

class Employee(BaseModel):
    employee_id: int
    name: str
    surname: str
    description: str


# -------- GET all employees --------
@app.get("/employees")
def get_employees():
    return get_employees_db()


# -------- GET single employee --------
@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    employee = get_employee_db(employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


# -------- POST add employee --------
@app.post("/employees")
def add_employee(employee: Employee):
    add_employee_db(
        employee.employee_id,
        employee.name,
        employee.surname,
        employee.description
    )
    return {"message": "Employee added successfully"}


# -------- PUT update employee --------
@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: Employee):
    update_employee_db(
        employee_id,
        employee.name,
        employee.surname,
        employee.description
    )
    return {"message": "Employee updated successfully"}


# -------- DELETE employee --------
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    delete_employee_db(employee_id)
    return {"message": "Employee deleted successfully"}


# Optional: export SDL via curl
@app.get("/schema.graphql")
def export_schema():
    return Response(schema.as_str(), media_type="text/plain")


# =====================================================
# GRAPHQL
# =====================================================

@strawberry.type
class EmployeeType:
    employee_id: int
    name: str
    surname: str
    description: str


@strawberry.type
class Query:

    @strawberry.field
    def employees(self) -> list[EmployeeType]:
        employees = get_employees_db()
        return [EmployeeType(**emp) for emp in employees]

    @strawberry.field
    def employee(self, employee_id: int) -> EmployeeType | None:
        employee = get_employee_db(employee_id)

        if employee:
            return EmployeeType(**employee)

        return None

#    @strawberry.field
#    def employee_by_surname( self, employee_surname: str ) -> EmployeeType | None:
#        employee = get_employee_by_surname_db( employee_surname )
#
#        if employee:
#            return EmployeeType( **employee )
#
#        return None

@strawberry.type
class Mutation:

    @strawberry.mutation
    def add_employee(self, employee_id: int, name: str, surname: str, description: str) -> str:
        add_employee_db(employee_id, name, surname, description)
        return "Employee added successfully"

    @strawberry.mutation
    def update_employee(self, employee_id: int, name: str, surname: str, description: str) -> str:
        update_employee_db(employee_id, name, surname, description)
        return "Employee updated successfully"

    @strawberry.mutation
    def delete_employee(self, employee_id: int) -> str:
        delete_employee_db(employee_id)
        return "Employee deleted successfully"


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")

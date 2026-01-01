"""
FastAPI Todo Application

A simple RESTful API for managing a todo list with SQLite database backend.
Supports full CRUD operations (Create, Read, Update, Delete) for todo items.

Author: Anubhav
Version: 1.0.0
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP

# Initialize FastAPI application with metadata for API documentation
app = FastAPI(
    title="Todo API",
    description="A simple RESTful API for managing todo items with SQLite database",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Database configuration
DATABASE_FILE = "todos.db"


# Database connection context manager for proper resource management
@contextmanager
def get_db_connection():
    """
    Context manager for SQLite database connections.
    Ensures proper connection handling and automatic cleanup.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database() -> None:
    """
    Initialize the database by creating the todos table if it doesn't exist.
    Called on application startup to ensure the database schema is ready.
    """
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                todo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
            """
        )


# Pydantic models for request/response validation and API documentation


class TodoCreate(BaseModel):
    """
    Schema for creating a new todo item.
    Used for POST /todos endpoint.
    """

    content: str = Field(..., description="The todo item content", min_length=1)
    completed: bool = Field(
        default=False, description="Whether the todo is completed"
    )


class TodoUpdate(BaseModel):
    """
    Schema for updating an existing todo item.
    Used for PUT /todos/{todo_id} endpoint.
    All fields are optional for partial updates.
    """

    content: Optional[str] = Field(
        None, description="The todo item content", min_length=1
    )
    completed: Optional[bool] = Field(
        None, description="Whether the todo is completed"
    )


class Todo(BaseModel):
    """
    Schema for todo item responses.
    Used for GET endpoints to structure the API response.
    """

    todo_id: int = Field(..., description="Unique identifier for the todo")
    content: str = Field(..., description="The todo item content")
    completed: bool = Field(
        default=False, description="Whether the todo is completed"
    )

    class Config:
        """Pydantic configuration for the Todo model."""

        from_attributes = True


# Helper function to convert database row to Todo model
def row_to_todo(row: sqlite3.Row) -> Todo:
    """
    Convert a SQLite Row object to a Todo Pydantic model.
    
    Args:
        row: SQLite Row object from database query
        
    Returns:
        Todo: Pydantic model instance
    """
    return Todo(
        todo_id=row["todo_id"],
        content=row["content"],
        completed=bool(row["completed"]),
    )


# API Endpoints


@app.on_event("startup")
async def startup_event() -> None:
    """
    Initialize the database when the application starts.
    This ensures the todos table exists before handling any requests.
    """
    init_database()


@app.get("/", tags=["Root"], operation_id="read_root")
async def read_root() -> JSONResponse:
    """
    Root endpoint that returns a welcome message.
    
    Returns:
        JSONResponse: Welcome message with API information
    """
    return JSONResponse(
        content={
            "message": "Welcome to the Todo API",
            "version": "1.0.0",
            "docs": "/docs",
        }
    )


@app.get(
    "/todos",
    response_model=List[Todo],
    status_code=status.HTTP_200_OK,
    tags=["Todos"],
    summary="Get all todos",
    description="Retrieve a list of all todo items from the database",
    operation_id="get_all_todos",
)
async def get_all_todos() -> List[Todo]:
    """
    Get all todo items from the database.
    
    Returns:
        List[Todo]: List of all todo items
    """
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM todos ORDER BY todo_id")
        rows = cursor.fetchall()
        return [row_to_todo(row) for row in rows]


@app.get(
    "/todos/{todo_id}",
    response_model=Todo,
    status_code=status.HTTP_200_OK,
    tags=["Todos"],
    summary="Get a specific todo",
    description="Retrieve a single todo item by its ID",
    operation_id="get_todo",
)
async def get_todo(todo_id: int) -> Todo:
    """
    Get a specific todo item by ID.
    
    Args:
        todo_id: The unique identifier of the todo item
        
    Returns:
        Todo: The todo item with the specified ID
        
    Raises:
        HTTPException: 404 if todo with given ID is not found
    """
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM todos WHERE todo_id = ?", (todo_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )
        return row_to_todo(row)


@app.post(
    "/todos",
    response_model=Todo,
    status_code=status.HTTP_201_CREATED,
    tags=["Todos"],
    summary="Create a new todo",
    description="Create a new todo item in the database",
    operation_id="create_todo",
)
async def create_todo(todo: TodoCreate) -> Todo:
    """
    Create a new todo item.
    
    Args:
        todo: TodoCreate model with content and optional completed status
        
    Returns:
        Todo: The newly created todo item with its generated ID
    """
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO todos (content, completed) VALUES (?, ?)",
            (todo.content, todo.completed),
        )
        todo_id = cursor.lastrowid
        # Fetch the newly created todo to return it
        cursor = conn.execute("SELECT * FROM todos WHERE todo_id = ?", (todo_id,))
        row = cursor.fetchone()
        return row_to_todo(row)


@app.put(
    "/todos/{todo_id}",
    response_model=Todo,
    status_code=status.HTTP_200_OK,
    tags=["Todos"],
    summary="Update a todo",
    description="Update an existing todo item by its ID (supports partial updates)",
    operation_id="update_todo",
)
async def update_todo(todo_id: int, todo_update: TodoUpdate) -> Todo:
    """
    Update an existing todo item.
    
    Args:
        todo_id: The unique identifier of the todo item to update
        todo_update: TodoUpdate model with fields to update (all optional)
        
    Returns:
        Todo: The updated todo item
        
    Raises:
        HTTPException: 404 if todo with given ID is not found
    """
    with get_db_connection() as conn:
        # Check if todo exists
        cursor = conn.execute("SELECT * FROM todos WHERE todo_id = ?", (todo_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )

        # Build update query dynamically based on provided fields
        updates = []
        params = []
        if todo_update.content is not None:
            updates.append("content = ?")
            params.append(todo_update.content)
        if todo_update.completed is not None:
            updates.append("completed = ?")
            params.append(todo_update.completed)

        if updates:
            params.append(todo_id)
            query = f"UPDATE todos SET {', '.join(updates)} WHERE todo_id = ?"
            conn.execute(query, params)

        # Fetch and return the updated todo
        cursor = conn.execute("SELECT * FROM todos WHERE todo_id = ?", (todo_id,))
        row = cursor.fetchone()
        return row_to_todo(row)


@app.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Todos"],
    summary="Delete a todo",
    description="Delete a todo item from the database by its ID",
    operation_id="delete_todo",
)
async def delete_todo(todo_id: int) -> None:
    """
    Delete a todo item by ID.
    
    Args:
        todo_id: The unique identifier of the todo item to delete
        
    Raises:
        HTTPException: 404 if todo with given ID is not found
    """
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM todos WHERE todo_id = ?", (todo_id,))
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )

# MCP Server
mcp = FastApiMCP(app, include_operations=["get_all_todos", "get_todo", "create_todo", "update_todo", "delete_todo"])
mcp.mount()
# FastAPI Todo Application

A modern RESTful API for managing todo items built with FastAPI and SQLite. This application provides a complete CRUD interface for todo management with integrated Model Context Protocol (MCP) support for AI-powered interactions.

## Overview

This project demonstrates a production-ready FastAPI application with:
- Full CRUD operations for todo items
- SQLite database backend with automatic schema initialization
- Pydantic models for request/response validation
- Interactive API documentation via Swagger UI and ReDoc
- MCP server integration for AI agent interactions
- Proper error handling and HTTP status codes

## Features

- **Create Todos**: Add new todo items with content and completion status
- **Read Todos**: Retrieve all todos or fetch a specific todo by ID
- **Update Todos**: Partially update todo items (content and/or completion status)
- **Delete Todos**: Remove todo items from the database
- **MCP Integration**: Expose API operations via Model Context Protocol for AI agents
- **Auto Documentation**: Interactive API docs available at `/docs` and `/redoc`
- **Type Safety**: Full type hints and Pydantic validation
- **Database Management**: Automatic schema initialization and connection handling

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLite**: Lightweight relational database
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running the application
- **FastAPI-MCP**: MCP server integration for FastAPI applications

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi-mcp-todo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or using uv:
```bash
uv pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Root Endpoint**: `http://localhost:8000/`

## API Endpoints

### Root

**GET** `/`

Returns a welcome message with API information.

**Response:**
```json
{
  "message": "Welcome to the Todo API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### Get All Todos

**GET** `/todos`

Retrieve a list of all todo items.

**Response:** `200 OK`
```json
[
  {
    "todo_id": 1,
    "content": "Complete project documentation",
    "completed": false
  },
  {
    "todo_id": 2,
    "content": "Review code changes",
    "completed": true
  }
]
```

### Get Todo by ID

**GET** `/todos/{todo_id}`

Retrieve a specific todo item by its ID.

**Parameters:**
- `todo_id` (path): Integer ID of the todo item

**Response:** `200 OK`
```json
{
  "todo_id": 1,
  "content": "Complete project documentation",
  "completed": false
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Todo with id {todo_id} not found"
}
```

### Create Todo

**POST** `/todos`

Create a new todo item.

**Request Body:**
```json
{
  "content": "New todo item",
  "completed": false
}
```

**Response:** `201 Created`
```json
{
  "todo_id": 3,
  "content": "New todo item",
  "completed": false
}
```

### Update Todo

**PUT** `/todos/{todo_id}`

Update an existing todo item. Supports partial updates.

**Parameters:**
- `todo_id` (path): Integer ID of the todo item

**Request Body:**
```json
{
  "content": "Updated content",
  "completed": true
}
```

Both fields are optional. You can update just `content` or just `completed`.

**Response:** `200 OK`
```json
{
  "todo_id": 1,
  "content": "Updated content",
  "completed": true
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Todo with id {todo_id} not found"
}
```

### Delete Todo

**DELETE** `/todos/{todo_id}`

Delete a todo item by its ID.

**Parameters:**
- `todo_id` (path): Integer ID of the todo item

**Response:** `204 No Content`

**Error Response:** `404 Not Found`
```json
{
  "detail": "Todo with id {todo_id} not found"
}
```

## MCP Integration

This application includes Model Context Protocol (MCP) server integration, allowing AI agents to interact with the API through standardized MCP operations. The following operations are exposed:

- `get_all_todos`: Retrieve all todo items
- `get_todo`: Get a specific todo by ID
- `create_todo`: Create a new todo item
- `update_todo`: Update an existing todo
- `delete_todo`: Delete a todo item

The MCP server is automatically mounted when the application starts.

## Database Schema

The application uses SQLite with the following schema:

```sql
CREATE TABLE todos (
    todo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 0
)
```

The database file (`todos.db`) is automatically created on first run. The schema is initialized during application startup.

## Project Structure

```
fastapi-mcp-todo/
├── main.py              # Main application file with all endpoints
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment configuration
├── todos.db             # SQLite database (created automatically)
└── README.md            # This file
```

## Development

### Running in Development Mode

For development with auto-reload:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Code Structure

- **Database Management**: Context manager for SQLite connections with proper transaction handling
- **Pydantic Models**: `TodoCreate`, `TodoUpdate`, and `Todo` for request/response validation
- **API Endpoints**: RESTful endpoints with proper HTTP status codes and error handling
- **MCP Server**: FastAPI-MCP integration for AI agent interactions

### Key Features

- Type hints throughout the codebase
- Comprehensive docstrings
- Proper error handling with HTTP exceptions
- Database connection pooling via context managers
- Automatic transaction rollback on errors

## Deployment

The project includes a `render.yaml` configuration file for deployment on Render.com. The application can be deployed to any platform that supports Python and ASGI applications.

### Render Deployment

The `render.yaml` file configures:
- Web service type
- Python environment
- Build command using uv
- Start command with uvicorn
- Free tier plan

## Testing the API

### Using curl

```bash
# Get all todos
curl http://localhost:8000/todos

# Get a specific todo
curl http://localhost:8000/todos/1

# Create a todo
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"content": "Test todo", "completed": false}'

# Update a todo
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete a todo
curl -X DELETE http://localhost:8000/todos/1
```

### Using Python requests

```python
import requests

# Get all todos
response = requests.get("http://localhost:8000/todos")
todos = response.json()
print(todos)

# Create a todo
new_todo = {
    "content": "New todo item",
    "completed": False
}
response = requests.post("http://localhost:8000/todos", json=new_todo)
print(response.json())
```

## License

This project is open source and available for educational purposes.

## Author

Anubhav

## Version

1.0.0

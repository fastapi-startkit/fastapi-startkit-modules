# FastAPI Application Example

This is a web application built using the `fastapi-startkit` framework. It demonstrates how to leverage the framework's features for building FastAPI-based APIs.

## Project Structure

- **`artisan`**: The main entry point for managing the application (e.g., serving the app).
- **`bootstrap/application.py`**: Initializes the `Application` container and registers service providers.
- **`providers/`**: Service providers responsible for registering routers, services, and other components.
- **`routes/`**: Contains the FastAPI router definitions.
- **`config/`**: Configuration files for various components like logging.

## Getting Started

### Prerequisites

Ensure you have [uv](https://github.com/astral-sh/uv) installed.

### Setup

1.  Sync dependencies:
    ```bash
    uv sync
    ```

### Running the Application

You can start the FastAPI server using the `serve` command:

```bash
uv run python artisan serve
```

By default, the application will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Features

- **FastAPI Integration**: Out-of-the-box support for FastAPI.
- **Built-in Logging**: Easily log messages with different levels.
- **Service Providers**: Modular way to register logic and routes.
- **Automatic Documentation**: Access Swagger UI at `/docs`.

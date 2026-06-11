# CV Matcher

FastAPI service for hybrid semantic search over CV/roster profiles (Qdrant RAG), with LangGraph agent support.

## Requirements

- Python 3.14+
- PostgreSQL
- uv (python package installer)
- make (build automation tool)

## Install python
```bash
pyenv install 3.14
```

## Installation

- ### Clone the repository
- ### Create and activate virtual environment

```bash
uv venv --python 3.14
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

- ### Init uv
```bash
uv init
```

- ### Install dependencies:

- #### Code Standards
```bash
uv add --dev basedpyright pydantic ruff
```
- **basedpyright** - static type checking
- **pydantic** - data validation
- **ruff** - linting and code formatting (`ruff check`, `ruff format`)

Ruff and basedpyright settings live in `pyproject.toml` under `[tool.ruff]` and `[tool.basedpyright]`.

- #### Fast API Core Dependencies
```bash
uv add "fastapi[standard]" pydantic-settings sqlalchemy sqlmodel
```

- ### Configure Fast API
- Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

## Development

1. Start the development server:

```bash
make run
```

2. Access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with:

```bash
pytest
```

## Code Quality

Format and lint:

```bash
ruff format .
ruff check .
```

Type checking:

```bash
basedpyright
```

Or run both via:

```bash
make lint
```

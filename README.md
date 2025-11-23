# Module 12 – FastAPI Calculator + User Auth

This project implements:

- User registration & login (hashed passwords)
- Calculation CRUD API with SQLAlchemy models & Pydantic schemas
- Calculation factory pattern (Add/Sub/Mul/Div)
- Full CI/CD pipeline running tests and pushing Docker images
- Integration tests using PostgreSQL (locally + GitHub Actions)

## 📦 Requirements

- Python 3.11
- PostgreSQL (local Docker)
- Virtual environment (recommended)
- Docker

## 🚀 Running Locally
1. Create & Activate Virtual Environment
```
python3.11 -m venv venv
source venv/bin/activate
```
2. Install Dependencies
```
pip install -r requirements.txt
```

## 🗄️ Local PostgreSQL for Integration Tests

Start Postgres

```
docker run --name test-postgres \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=testdb \
    -p 5432:5432 -d postgres:16
```
## 🧪 Running Tests Locally
Run ALL tests
```
pytest tests/ -v --disable-warnings
```
▶️ Running the FastAPI App Locally
```
uvicorn app.main:app --reload
```

## 🐳 Docker Image

Docker Hub Repository

👉 YOUR_DOCKER_HUB_REPO_LINK_HERE

## ✔️ Features Implemented
- SQLAlchemy Calculation model
- Pydantic schemas with validation
- Division by zero checks
- Operation factory pattern
- Unit + Integration tests
- CI/CD with DB + test automation
- Module 12
- User registration + login (hashed passwords via passlib)
- Calculation CRUD API endpoints
- Full test coverage
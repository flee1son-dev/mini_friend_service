# mini_friend_service

- Минималистичный REST API сервис для управления пользователями, авторизацией и дружбой между пользователями.



# Technology stack:
- Python 3.13
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Alembic (database migration)
- Docker / Docker Compose
- Uvicorn (ASGI server)
- unittests


# Project Features

- JWT authentication

- User registration and login

- Friendship system

- PostgreSQL database

- Alembic migrations

- Dockerized environment

- Integration and unit tests

- Modular architecture


# Project architecture
    ├── README.md
├── backend
│   ├── Dockerfile
│   ├── __init__.py
│   ├── alembic
│   │   ├── README
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions
│   ├── alembic.ini
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   └── security.py
│   ├── main.py
│   ├── modules
│   │   ├── __init__.py
│   │   ├── auth
│   │   ├── friendships
│   │   └── users
│   └── requirements.txt
├── docker-compose.yml
└── tests
    ├── __init__.py
    ├── data
    ├── test_base.py
    ├── test_integration
    │   ├── __init__.py
    │   ├── test_auth_routers.py
    │   ├── test_friendships_routers.py
    │   └── test_users_routers.py
    ├── test_unit
    │   ├── __init__.py
    │   ├── test_auth_services.py
    │   ├── test_friendships_services.py
    │   └── test_users_services.py
    └── utils
        ├── __init__.py
        ├── auth_helpers.py
        └── test_cleint.py

22 directories, 33 files


# Getting Started

## Clone Repository

```bash

git clone https://github.com/flee1son-dev/mini_friend_service.git

cd mini_friend_service

```


# Environment Variables

Create '.env' file inside the project root:

```.env

SECRET_KEY=secret_key
DATABASE_URL=postgresql://postgres:postgres@(db & localhost):5432/mini_friend_services
DEBUG=True
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=mini_friend_services
POSTGRES_HOST=db & localhost

```

# Docker build and run
```bash

docker-compose up --build

```
After launch, the service will be available at:

- API: http://localhost:8000

- Swagger Docs: http://localhost:8000/docs

- ReDoc: http://localhost:8000/redoc


# Local Development

## Environment Variables for local dev
-create .env file in backend folder 

## Create Virtual Environment

```bash

python -m venv venv

```

## Activate Environment

### Linux / macOS

```bash

source venv/bin/activate

```

### Windows

```bash

venv\Scripts\activate

```

## Install Dependencies

```bash

pip install -r backend/requirements.txt

```

## Run PostgreSQL

Make sure PostgreSQL is running locally.

## Apply Migrations

```bash

cd backend

alembic upgrade head

```

## Run Application

```bash

uvicorn backend.main:app --reload 

```


# Running tests

## Run all tests
```bash

python3 -m unittest discover

```

## Run Unit tests
```bash

python3 -m unittest tests.test_unit

```

## Run Integration tests
```bash

python3 -m unittest tests.test_integration

```


# API Modules

## Auth Module

- User registration

- User login

- JWT token generation

- Password hashing

## Users Module

- Get user info

- Update profile

- User management

## Friendships Module

- Send friend request

- Accept friendship

- Remove friend

- Get friends list


# Security

Project uses:

- JWT Authentication

- Password hashing

- Protected routes

- Dependency injection for authorization


# Future Improvements

- Redis caching

- Async SQLAlchemy

- Celery background tasks

- CI/CD pipeline

- WebSocket notifications

- Email verification

- Refresh tokens

- Pagination

- Rate limiting


# Development Standards

- PEP8

- Modular architecture

- Layered structure

- Separation of concerns

- Unit testing

- Integration testing


# Requirements

Example `requirements.txt`:

```txt

fastapi
uvicorn
sqlalchemy
psycopg2-binary
alembic
python-jose
passlib[bcrypt]
pydantic
pytest
httpx

```


# Author

Shmidt Nikita Andreevich

- GitHub: flee1son-dev
- Project: Mini Friend Service


# License

MIT License
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import get_db


def create_test_client(db_session):

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from securebank.database import Base, get_db
from securebank.main import app

TEST_DATABASE_URL = (
    "postgresql+psycopg://securebank:securebank123@localhost:5433/securebank_test"
)


test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    test_engine.dispose()
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    test_engine.dispose()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def mock_rate_limit(mocker):
    mocker.patch("securebank.routers.auth.check_login_rate_limit")
    mocker.patch("securebank.routers.auth.clear_failed_logins")
    mocker.patch("securebank.routers.auth.record_failed_login")

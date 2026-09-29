from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import verify_password, create_access_token
from app.modules.auth.models import User, RefreshToken
from app.modules.transporter.profile.models import TransporterProfile
from app.modules.transporter.vehicles.models import Vehicle


@pytest.fixture
def auth_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    def override():
        with factory() as session:
            yield session
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override
    with TestClient(app) as client:
        yield client, factory
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)
    engine.dispose()


def registration(**changes):
    return dict(name="Registered Transporter", email="registered@example.com", mobile="9000000011",
                password="Test-only-secret!", vehicleType="Truck", vehicleNumber="QA-REG-1",
                capacity="5-10 Tons", city="Chennai", state="Tamil Nadu", **changes)


def register(client):
    response = client.post("/api/v1/auth/register", json=registration())
    assert response.status_code == 200, response.text
    assert "password_hash" not in response.text
    return response.json()["data"]


def test_register_persists_and_original_credentials_login(auth_db):
    client, factory = auth_db
    result = register(client)
    with factory() as db:
        user = db.query(User).filter_by(email="registered@example.com").one()
        assert verify_password(registration()["password"], user.password_hash)
        assert user.password_hash != registration()["password"]
        assert db.query(TransporterProfile).filter_by(user_id=user.id).one().contact_person == user.name
        assert db.query(Vehicle).filter_by(transporter_id=user.id).one().vehicle_number == "QA-REG-1"
    # Registration and repeated logins within one second must not collide.
    for _ in range(2):
        response = client.post("/api/v1/auth/login", json={"email": " REGISTERED@EXAMPLE.COM ", "password": registration()["password"]})
        assert response.status_code == 200
        token = response.json()["data"]["access_token"]
        me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.json()["data"]["id"] == result["user"]["id"]
        assert "password_hash" not in me.text


@pytest.mark.parametrize("email,password", [("registered@example.com", "incorrect"), ("unknown@example.com", "incorrect")])
def test_wrong_credentials_rejected(auth_db, email, password):
    client, _ = auth_db
    register(client)
    assert client.post("/api/v1/auth/login", json={"email": email, "password": password}).status_code == 401


@pytest.mark.parametrize("duplicate", ["email", "mobile", "vehicleNumber"])
def test_duplicate_registration_leaves_no_partial_user(auth_db, duplicate):
    client, factory = auth_db
    register(client)
    payload = registration()
    payload.update(email="second@example.com", mobile="9000000022", vehicleNumber="QA-REG-2")
    payload[duplicate] = registration()[duplicate]
    assert client.post("/api/v1/auth/register", json=payload).status_code in [400, 409]
    with factory() as db:
        assert db.query(User).count() == 1
        assert db.query(TransporterProfile).count() == 1
        assert db.query(Vehicle).count() == 1


def test_registration_validation(auth_db):
    client, factory = auth_db
    for field, value in [("password", "short"), ("mobile", "123"), ("name", " "), ("email", "invalid")]:
        payload = registration()
        payload[field] = value
        assert client.post("/api/v1/auth/register", json=payload).status_code == 422
    with factory() as db:
        assert db.query(User).count() == 0


def test_refresh_rotation_logout_and_expiry(auth_db):
    client, factory = auth_db
    data = register(client)
    old = data["refresh_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": old})
    assert response.status_code == 200
    new = response.json()["data"]["refresh_token"]
    assert new != old
    assert len(new) <= 255
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": old}).status_code == 401
    assert client.post("/api/v1/auth/logout", json={"refresh_token": new}).status_code == 200
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": new}).status_code == 401
    with factory() as db:
        expired = db.query(RefreshToken).filter_by(token=new).one()
        expired.is_revoked = False
        expired.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        db.commit()
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": new}).status_code == 401


@pytest.mark.parametrize("field,value", [("role", "BUYER"), ("status", "INACTIVE")])
def test_unavailable_account_cannot_login_or_refresh(auth_db, field, value):
    client, factory = auth_db
    data = register(client)
    with factory() as db:
        user = db.get(User, data["user"]["id"])
        setattr(user, field, value)
        db.commit()
    assert client.post("/api/v1/auth/login", json={"email": registration()["email"], "password": registration()["password"]}).status_code == 403
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": data["refresh_token"]}).status_code == 401


def test_protected_api_and_health(auth_db):
    client, _ = auth_db
    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.get("/api/v1/transporter/profile").status_code == 401

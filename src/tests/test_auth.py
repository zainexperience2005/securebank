def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Zain Ul Islam",
            "email": "zain@example.com",
            "password": "securebank123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Zain Ul Islam"
    assert data["email"] == "zain@example.com"

    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_email_not_allowed(client):
    user_data = {
        "full_name": "Zain Ul Islam",
        "email": "zain@example.com",
        "password": "securebank123",
    }

    first_response = client.post(
        "/auth/register",
        json=user_data,
    )

    second_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json()["detail"] == (
        "Email is already registered"
    )

def test_login_success(client, mocker):
    mocker.patch(
        "securebank.routers.auth.check_login_rate_limit"
    )
    mocker.patch(
        "securebank.routers.auth.clear_failed_logins"
    )
    mocker.patch(
        "securebank.routers.auth.record_failed_login"
    )

    client.post(
        "/auth/register",
        json={
            "full_name": "Zain Ul Islam",
            "email": "zain@example.com",
            "password": "securebank123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "zain@example.com",
            "password": "securebank123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, mocker):
    mocker.patch(
        "securebank.routers.auth.check_login_rate_limit"
    )

    failed_login = mocker.patch(
        "securebank.routers.auth.record_failed_login"
    )

    client.post(
        "/auth/register",
        json={
            "full_name": "Zain Ul Islam",
            "email": "zain@example.com",
            "password": "securebank123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "zain@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Incorrect email or password"
    )

    failed_login.assert_called_once()


def test_login_user_not_found(client, mocker):
    mocker.patch(
        "securebank.routers.auth.check_login_rate_limit"
    )

    failed_login = mocker.patch(
        "securebank.routers.auth.record_failed_login"
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "somepassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Incorrect email or password"
    )

    failed_login.assert_called_once()


def test_get_current_user(client, mocker):
    mocker.patch(
        "securebank.routers.auth.check_login_rate_limit"
    )
    mocker.patch(
        "securebank.routers.auth.clear_failed_logins"
    )
    mocker.patch(
        "securebank.routers.auth.record_failed_login"
    )

    client.post(
        "/auth/register",
        json={
            "full_name": "Zain Ul Islam",
            "email": "zain@example.com",
            "password": "securebank123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "zain@example.com",
            "password": "securebank123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["full_name"] == "Zain Ul Islam"
    assert data["email"] == "zain@example.com"


def test_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401


def test_missing_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401

    
from sqlalchemy import select

from securebank.models import User


def register_and_login(
    client,
    email="zain@example.com",
):
    password = "securebank123"

    client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "password": password,
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

def test_customer_cannot_freeze_account(
    client,
):
    headers = register_and_login(
        client,
        email="customer@example.com",
    )

    account = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=headers,
    ).json()

    response = client.patch(
        f"/accounts/{account['id']}/status",
        json={"is_active": False},
        headers=headers,
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "Admin access required"
    )

def test_admin_can_freeze_account(
    client,
    db_session,
):
    customer_headers = register_and_login(
        client,
        email="customer@example.com",
    )

    account = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=customer_headers,
    ).json()

    admin_headers = register_and_login(
        client,
        email="admin@example.com",
    )

    admin = db_session.scalar(
        select(User).where(
            User.email == "admin@example.com"
        )
    )

    admin.role = "admin"

    db_session.commit()

    response = client.patch(
        f"/accounts/{account['id']}/status",
        json={"is_active": False},
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_active"] is False

    unfreeze_response = client.patch(
        f"/accounts/{account['id']}/status",
        json={"is_active": True},
        headers=admin_headers,
    )

    assert unfreeze_response.status_code == 200
    assert unfreeze_response.json()["is_active"] is True


def test_frozen_account_cannot_withdraw(
    client,
    db_session,
):
    customer_headers = register_and_login(
        client,
        email="customer@example.com",
    )

    account = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=customer_headers,
    ).json()

    client.post(
        "/transactions/deposit",
        json={
            "account_id": account["id"],
            "amount": "5000.00",
        },
        headers=customer_headers,
    )

    admin_headers = register_and_login(
        client,
        email="admin@example.com",
    )

    admin = db_session.scalar(
        select(User).where(
            User.email == "admin@example.com"
        )
    )

    admin.role = "admin"
    db_session.commit()

    client.patch(
        f"/accounts/{account['id']}/status",
        json={"is_active": False},
        headers=admin_headers,
    )

    response = client.post(
        "/transactions/withdraw",
        json={
            "account_id": account["id"],
            "amount": "1000.00",
        },
        headers=customer_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Account is not active"



def test_freeze_account_creates_audit_log(
    client,
    db_session,
    mock_rate_limit,
):
    customer_headers = register_and_login(
        client,
        email="customer@example.com",
    )

    account = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=customer_headers,
    ).json()

    admin_headers = register_and_login(
        client,
        email="admin@example.com",
    )

    admin = db_session.scalar(
        select(User).where(
            User.email == "admin@example.com"
        )
    )

    admin.role = "admin"
    db_session.commit()

    freeze_response = client.patch(
        f"/accounts/{account['id']}/status",
        json={"is_active": False},
        headers=admin_headers,
    )

    assert freeze_response.status_code == 200

    logs_response = client.get(
        "/admin/audit-logs",
        headers=admin_headers,
    )

    assert logs_response.status_code == 200

    logs = logs_response.json()

    assert len(logs) == 1

    assert logs[0]["action"] == "freeze_account"
    assert logs[0]["target_type"] == "bank_account"
    assert logs[0]["target_id"] == account["id"]



def test_customer_cannot_view_audit_logs(
    client,
    mock_rate_limit,
):
    headers = register_and_login(
        client,
        email="customer@example.com",
    )

    response = client.get(
        "/admin/audit-logs",
        headers=headers,
    )

    assert response.status_code == 403
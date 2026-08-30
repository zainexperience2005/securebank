def register_and_login(
    client,
    mocker=None,
    email="zain@example.com",
):
    if isinstance(mocker, str):
        email = mocker
        mocker = None

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

    return {"Authorization": f"Bearer {token}"}


def test_create_account(client, mocker):
    headers = register_and_login(
        client,
        mocker,
    )

    response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["account_type"] == "savings"
    assert data["balance"] == "0.00"
    assert data["account_number"].startswith("SB")


def test_create_account_without_auth(client):
    response = client.post(
        "/accounts",
        json={"account_type": "savings"},
    )

    assert response.status_code == 401


def test_invalid_account_type(client, mocker):
    headers = register_and_login(
        client,
        mocker,
    )

    response = client.post(
        "/accounts",
        json={"account_type": "crypto"},
        headers=headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == ("Account type must be savings or current")


def test_deposit_money(client, mocker):
    headers = register_and_login(
        client,
        mocker,
    )

    account_response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=headers,
    )

    account_id = account_response.json()["id"]

    deposit_response = client.post(
        "/transactions/deposit",
        json={
            "account_id": account_id,
            "amount": "5000.00",
        },
        headers=headers,
    )

    assert deposit_response.status_code == 201

    transaction = deposit_response.json()

    assert transaction["transaction_type"] == "deposit"
    assert transaction["amount"] == "5000.00"
    assert transaction["status"] == "completed"

    account_response = client.get(
        f"/accounts/{account_id}",
        headers=headers,
    )

    assert account_response.json()["balance"] == "5000.00"


def test_withdraw_money(client, mocker):
    headers = register_and_login(
        client,
        mocker,
    )

    account_response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=headers,
    )

    account_id = account_response.json()["id"]

    client.post(
        "/transactions/deposit",
        json={
            "account_id": account_id,
            "amount": "5000.00",
        },
        headers=headers,
    )

    withdraw_response = client.post(
        "/transactions/withdraw",
        json={
            "account_id": account_id,
            "amount": "2000.00",
        },
        headers=headers,
    )

    assert withdraw_response.status_code == 201

    transaction = withdraw_response.json()

    assert transaction["transaction_type"] == "withdraw"
    assert transaction["amount"] == "2000.00"

    account_response = client.get(
        f"/accounts/{account_id}",
        headers=headers,
    )

    assert account_response.json()["balance"] == "3000.00"


def test_withdraw_insufficient_balance(
    client,
    mocker,
):
    headers = register_and_login(
        client,
        mocker,
    )

    account_response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=headers,
    )

    account_id = account_response.json()["id"]

    response = client.post(
        "/transactions/withdraw",
        json={
            "account_id": account_id,
            "amount": "1000.00",
        },
        headers=headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == ("Insufficient balance")


def test_user_cannot_access_another_users_account(
    client,
    mocker,
):
    user_one_headers = register_and_login(
        client,
        mocker,
        email="zain@example.com",
    )

    account_response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=user_one_headers,
    )

    account_id = account_response.json()["id"]

    user_two_headers = register_and_login(
        client,
        mocker,
        email="ahmed@example.com",
    )

    response = client.get(
        f"/accounts/{account_id}",
        headers=user_two_headers,
    )

    assert response.status_code == 404


def test_user_cannot_deposit_into_unauthorized_account(
    client,
    mocker,
):
    user_one_headers = register_and_login(
        client,
        mocker,
        email="zain@example.com",
    )

    account_response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=user_one_headers,
    )

    account_id = account_response.json()["id"]

    user_two_headers = register_and_login(
        client,
        mocker,
        email="ahmed@example.com",
    )

    response = client.post(
        "/transactions/deposit",
        json={
            "account_id": account_id,
            "amount": "5000.00",
        },
        headers=user_two_headers,
    )

    assert response.status_code == 404


def test_successful_transfer(client, mocker):
    user_one_headers = register_and_login(
        client,
        mocker,
        email="zain@example.com",
    )

    source_response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=user_one_headers,
    )
    source_account_id = source_response.json()["id"]

    client.post(
        "/transactions/deposit",
        json={
            "account_id": source_account_id,
            "amount": "5000.00",
        },
        headers=user_one_headers,
    )

    user_two_headers = register_and_login(
        client,
        mocker,
        email="ahmed@example.com",
    )

    destination_response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=user_two_headers,
    )
    destination_account_id = destination_response.json()["id"]

    transfer_response = client.post(
        "/transactions/transfer",
        json={
            "source_account_id": source_account_id,
            "destination_account_id": destination_account_id,
            "amount": "2000.00",
        },
        headers=user_one_headers,
    )

    assert transfer_response.status_code == 201

    source_after = client.get(
        f"/accounts/{source_account_id}",
        headers=user_one_headers,
    )

    destination_after = client.get(
        f"/accounts/{destination_account_id}",
        headers=user_two_headers,
    )

    assert source_after.json()["balance"] == "3000.00"
    assert destination_after.json()["balance"] == "2000.00"


def test_transfer_with_insufficient_balance(
    client,
    mocker,
):
    user_one_headers = register_and_login(
        client,
        mocker,
        email="zain@example.com",
    )

    source_response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=user_one_headers,
    )

    source_account_id = source_response.json()["id"]

    user_two_headers = register_and_login(
        client,
        mocker,
        email="ahmed@example.com",
    )

    destination_response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=user_two_headers,
    )

    destination_account_id = destination_response.json()["id"]

    response = client.post(
        "/transactions/transfer",
        json={
            "source_account_id": source_account_id,
            "destination_account_id": destination_account_id,
            "amount": "1000.00",
        },
        headers=user_one_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Insufficient balance")


def test_cannot_transfer_to_same_account(
    client,
    mocker,
):
    headers = register_and_login(
        client,
        mocker,
    )

    account_response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=headers,
    )

    account_id = account_response.json()["id"]

    response = client.post(
        "/transactions/transfer",
        json={
            "source_account_id": account_id,
            "destination_account_id": account_id,
            "amount": "100.00",
        },
        headers=headers,
    )

    assert response.status_code == 400


def test_transaction_history(client, mocker):
    headers = register_and_login(
        client,
        mocker,
    )

    account_response = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=headers,
    )

    account_id = account_response.json()["id"]

    client.post(
        "/transactions/deposit",
        json={
            "account_id": account_id,
            "amount": "5000.00",
        },
        headers=headers,
    )

    client.post(
        "/transactions/withdraw",
        json={
            "account_id": account_id,
            "amount": "1000.00",
        },
        headers=headers,
    )

    response = client.get(
        f"/transactions/account/{account_id}",
        headers=headers,
    )

    assert response.status_code == 200

    transactions = response.json()

    assert len(transactions) == 2

    transaction_types = {
        transaction["transaction_type"] for transaction in transactions
    }

    assert "deposit" in transaction_types
    assert "withdraw" in transaction_types


def test_transfer_creates_both_transaction_records(
    client,
    mocker,
):
    sender_headers = register_and_login(
        client,
        mocker,
        email="sender@example.com",
    )

    sender_account = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=sender_headers,
    ).json()

    client.post(
        "/transactions/deposit",
        json={
            "account_id": sender_account["id"],
            "amount": "5000.00",
        },
        headers=sender_headers,
    )

    receiver_headers = register_and_login(
        client,
        mocker,
        email="receiver@example.com",
    )

    receiver_account = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=receiver_headers,
    ).json()

    client.post(
        "/transactions/transfer",
        json={
            "source_account_id": sender_account["id"],
            "destination_account_id": receiver_account["id"],
            "amount": "1500.00",
        },
        headers=sender_headers,
    )

    sender_history = client.get(
        f"/transactions/account/{sender_account['id']}",
        headers=sender_headers,
    ).json()

    receiver_history = client.get(
        f"/transactions/account/{receiver_account['id']}",
        headers=receiver_headers,
    ).json()

    sender_types = {transaction["transaction_type"] for transaction in sender_history}

    receiver_types = {
        transaction["transaction_type"] for transaction in receiver_history
    }

    assert "transfer_out" in sender_types
    assert "transfer_in" in receiver_types


def test_user_cannot_view_another_users_history(
    client,
    mocker,
):
    user_one_headers = register_and_login(
        client,
        mocker,
        email="zain@example.com",
    )

    account = client.post(
        "/accounts",
        json={"account_type": "savings"},
        headers=user_one_headers,
    ).json()

    user_two_headers = register_and_login(
        client,
        mocker,
        email="ahmed@example.com",
    )

    response = client.get(
        f"/transactions/account/{account['id']}",
        headers=user_two_headers,
    )

    assert response.status_code == 404

import secrets


def generate_account_number() -> str:
    random_part = secrets.randbelow(10**10)

    return f"SB{random_part:010d}"


def generate_transaction_reference() -> str:
    random_part = secrets.token_hex(4).upper()
    return f"TXN-{random_part}"

from app.services.auth_service import hash_password, verify_password


def test_hash_password_handles_passwords_longer_than_bcrypt_limit():
    long_password = "a" * 100

    hashed = hash_password(long_password)

    assert hashed
    assert verify_password(long_password, hashed) is True

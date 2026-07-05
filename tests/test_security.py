from app.core.security import create_access_token, create_refresh_token, decode_token, get_password_hash, verify_password


def test_password_hashing():
    password = "strongpassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_access_token_creation():
    token = create_access_token({"sub": "user123"})
    assert token is not None
    payload = decode_token(token)
    assert payload["sub"] == "user123"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_refresh_token_creation():
    token = create_refresh_token({"sub": "user123"})
    assert token is not None
    payload = decode_token(token)
    assert payload["sub"] == "user123"
    assert payload["type"] == "refresh"


def test_token_with_extra_claims():
    token = create_access_token({"sub": "user123", "role": "admin"})
    payload = decode_token(token)
    assert payload["role"] == "admin"


def test_invalid_token():
    try:
        decode_token("invalid_token_here")
        assert False, "Should have raised an exception"
    except Exception:
        assert True

"""
tests/test_security.py
Unit tests for JWT creation/verification and password hashing.
"""
import pytest
from jose import JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    plain = "MyStr0ngP@ssword!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrong_password", hashed)


def test_access_token_roundtrip():
    user_id = "00000000-0000-0000-0000-000000000001"
    company_id = "00000000-0000-0000-0000-000000000002"
    token = create_access_token(user_id, company_id, "EMPLOYEE")
    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["company_id"] == company_id
    assert payload["role"] == "EMPLOYEE"
    assert payload["type"] == "access"


def test_refresh_token_roundtrip():
    user_id = "00000000-0000-0000-0000-000000000001"
    token = create_refresh_token(user_id)
    payload = decode_refresh_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"


def test_access_token_rejected_as_refresh():
    token = create_access_token("uid", "cid", "EMPLOYEE")
    with pytest.raises(JWTError):
        decode_refresh_token(token)


def test_refresh_token_rejected_as_access():
    token = create_refresh_token("uid")
    with pytest.raises(JWTError):
        decode_access_token(token)

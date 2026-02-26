import pytest
from app.core.security import verify_password, get_password_hash, create_access_token

@pytest.fixture
def raw_password():
    return "Hello@123"

def test_password_hash(raw_password):
    assert raw_password!=get_password_hash(raw_password)

    hashed=get_password_hash(raw_password)
    assert verify_password(raw_password, hashed) is True

    assert verify_password("wrong@123", hashed) is False

def test_password_salting(raw_password):

    hashed1=get_password_hash(raw_password)
    hashed2=get_password_hash(raw_password)

    assert hashed1 != hashed2
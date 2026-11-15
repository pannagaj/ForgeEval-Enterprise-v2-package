from app.core.security import hash_password, verify_password, create_token, token_subject

def test_password_hash_round_trip():
    encoded = hash_password("a-long-test-password")
    assert encoded != "a-long-test-password"
    assert verify_password("a-long-test-password", encoded)
    assert not verify_password("wrong-password", encoded)

def test_token_subject():
    token = create_token("42")
    assert token_subject(token) == "42"
    assert token_subject("not-a-token") is None

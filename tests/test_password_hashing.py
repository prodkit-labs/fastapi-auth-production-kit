from prodkit_auth.security import (
    hash_password,
    hash_password_argon2id,
    verify_password,
    verify_password_any,
    verify_password_argon2id,
)


def test_bcrypt_hashing_still_verifies_password() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert password_hash.startswith("$2")
    assert verify_password("correct horse battery staple", password_hash)
    assert verify_password_any("correct horse battery staple", password_hash)


def test_argon2id_hashing_track_verifies_password() -> None:
    password_hash = hash_password_argon2id("correct horse battery staple")

    assert password_hash.startswith("$argon2")
    assert verify_password_argon2id("correct horse battery staple", password_hash)
    assert verify_password_any("correct horse battery staple", password_hash)


def test_argon2id_track_accepts_long_passwords() -> None:
    long_password = "x" * 120
    password_hash = hash_password_argon2id(long_password)

    assert verify_password_argon2id(long_password, password_hash)

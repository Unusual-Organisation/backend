from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

ph = PasswordHasher()


def hash_password(password: str) -> str:
    return ph.hash(password)


def check_password(hash: str, password: str) -> bool:
    try:
        ph.verify(hash, password)
    except VerificationError:
        return False
    else:
        return True

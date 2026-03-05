from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw_password) -> str:
    """Uses bcrypt to hash the password"""
    return password_context.hash(raw_password)


def verify_hashed_password(raw_password, hashed_password) -> bool:
    return password_context.verify(raw_password, hashed_password)

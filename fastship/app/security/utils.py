##  this is used to generate passwoord hash and and verify them
## hashing is cpu boundtherefore it cant be async -> it will block the event loop for that worker
from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_hash(password: str):
    # hash the password
    return context.hash(password)


def verify_hash_password(password: str, hashed_password: str):
    return context.verify(password, hashed_password)

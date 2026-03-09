from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=2,  # number of iterations or how many times the algo repeats
    memory_cost=65536,  # 64MB RAM required per hash
    parallelism=2,  # threads
)


def hash_password(raw_password) -> str:
    """Uses Argon2 to hash the password"""
    return ph.hash(raw_password)


def verify_hashed_password(raw_password, hashed_password) -> bool:
    try:
        return ph.verify(hashed_password, raw_password)
    except:
        return False

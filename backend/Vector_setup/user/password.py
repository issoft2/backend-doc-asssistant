from passlib.context import CryptContext

# configure bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # guard against None and overlong inputs
    safe = (password or "")[:64]
    return pwd_context.hash(safe)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

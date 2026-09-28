from sqlalchemy import or_
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime , timedelta
from passlib.context import CryptContext
from app.models.user import User,UserRole
from app.schemas.user import UserCreate
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")


def _normalize_bcrypt_password(password: str) -> str:
    if password is None:
        return ""

    encoded = password.encode("utf-8")
    if len(encoded) <= 72:
        return password

    return encoded[:72].decode("utf-8", errors="ignore")


def hash_password(password:str) -> str:
    normalized_password = _normalize_bcrypt_password(password)
    return pwd_context.hash(normalized_password)


def verify_password(plain: str, hashed: str) -> bool:
    normalized_plain = _normalize_bcrypt_password(plain)
    return pwd_context.verify(normalized_plain, hashed)

def create_access_token(user_id:int) -> str:
    expire=datetime.utcnow()+timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub":str(user_id),"exp":expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def signup_user(db:Session,user_data:UserCreate):
    if db.query(User).filter(User.email == user_data.email).first():
        return None, "Email already registered"

    if db.query(User).filter(User.username == user_data.username).first():
        return None, "Username already taken"

    if user_data.role not in UserRole.ALL:
        return None, "Invalid role"

    new_user = User(
        name=user_data.name,
        username=user_data.username.lower(),
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user , None

def login_user(db:Session, username_or_email:str, password:str):
    identifier = (username_or_email or "").strip()
    normalized_identifier = identifier.lower()

    user = db.query(User).filter(
        or_(
            User.email.ilike(identifier),
            User.username == normalized_identifier,
        )
    ).first()

    if not user or not verify_password(password,user.password_hash):
        return None, "Invalid email or password"
    
    if not user.is_active:
        return None , "Account is deactivated"
    
    token = create_access_token(user.id)
    return {
        "access_token":token,
        "token_type":"bearer",
        "user":user.to_dict()
    },None

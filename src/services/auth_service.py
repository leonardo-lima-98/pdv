from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from ..models.user import User
from ..schemas.user import UserCreate
import os

# Configurações de segurança
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto para hash de senhas - usando pbkdf2_sha256 por ser mais compatível
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha plain corresponde ao hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Autentica usuário por email e senha"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    # Truncar senha para 72 caracteres (limite bcrypt)
    password = password[:72] if len(password) > 72 else password
    if not verify_password(password, user.senha_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_user(db: Session, user_data: UserCreate) -> User:
    """Cria novo usuário"""
    # Verificar se perfil é válido
    if user_data.perfil not in ["vendedor", "gerente"]:
        raise ValueError("Perfil deve ser 'vendedor' ou 'gerente'")

    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ValueError("Email já cadastrado")

    # Criar usuário - truncar senha para 72 caracteres (limite bcrypt)
    password = user_data.senha[:72] if len(user_data.senha) > 72 else user_data.senha
    hashed_password = get_password_hash(password)
    user = User(
        nome=user_data.nome,
        email=user_data.email,
        senha_hash=hashed_password,
        perfil=user_data.perfil
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_current_user(token: str, db: Session) -> Optional[User]:
    """Obtém usuário atual do token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.email == email).first()
    return user

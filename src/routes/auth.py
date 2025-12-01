from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import authenticate_user, create_access_token, create_user, get_current_user
from ..schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from ..models import User

router = APIRouter(prefix="/auth", tags=["autenticação"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Faz login e retorna token JWT"""
    user = authenticate_user(db, request.email, request.senha)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )

    access_token = create_access_token(data={"sub": user.email})
    return TokenResponse(access_token=access_token, user=user)

@router.post("/logout")
def logout():
    """Logout - cliente deve descartar o token"""
    return {"message": "Logout realizado com sucesso"}

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registra novo usuário (apenas para desenvolvimento)"""
    try:
        user = create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

async def get_current_active_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependência para obter usuário atual"""
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )
    return user

def require_manager(current_user: User = Depends(get_current_active_user)):
    """Dependência para requerer perfil de gerente"""
    if current_user.perfil != "gerente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas gerentes podem acessar esta funcionalidade"
        )
    return current_user

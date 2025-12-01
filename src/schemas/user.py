from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    nome: str
    email: EmailStr
    perfil: str  # 'vendedor' ou 'gerente'

class UserCreate(UserBase):
    senha: str

    @field_validator('senha')
    @classmethod
    def validate_password_length(cls, v):
        # Truncar senha para 72 caracteres (limite bcrypt)
        if len(v) > 72:
            return v[:72]
        return v

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    perfil: Optional[str] = None
    ativo: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

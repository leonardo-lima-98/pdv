from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    nome: str
    codigo_barras: Optional[str] = None
    preco: float
    estoque: float = 0.0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    nome: Optional[str] = None
    codigo_barras: Optional[str] = None
    preco: Optional[float] = None
    estoque: Optional[float] = None
    ativo: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True

class StockEntry(BaseModel):
    produto_id: int
    quantidade: float

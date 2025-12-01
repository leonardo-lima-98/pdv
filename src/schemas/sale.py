from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SaleItemBase(BaseModel):
    produto_id: int
    quantidade: float

class SaleItemCreate(SaleItemBase):
    pass

class SaleItemResponse(BaseModel):
    id: int
    produto_id: int
    quantidade: float
    preco_unitario: float
    subtotal: float
    produto_nome: str

    class Config:
        from_attributes = True

class SaleCreate(BaseModel):
    itens: List[SaleItemCreate]
    metodo_pagamento: str  # 'dinheiro', 'cartao', 'pix'

class SaleResponse(BaseModel):
    id: int
    data_hora: datetime
    usuario_id: int
    usuario_nome: str
    total: float
    metodo_pagamento: str
    status: str
    itens: List[SaleItemResponse]

    class Config:
        from_attributes = True

class SaleSummary(BaseModel):
    id: int
    data_hora: datetime
    usuario_nome: str
    total: float
    metodo_pagamento: str
    status: str

    class Config:
        from_attributes = True

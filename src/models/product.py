from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base

class Product(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    codigo_barras = Column(String, unique=True, index=True, nullable=True)
    preco = Column(Float, nullable=False)
    estoque = Column(Float, default=0.0)  # Pode ser quantidade fracionária
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

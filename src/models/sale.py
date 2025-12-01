from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Sale(Base):
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now())
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    total = Column(Float, nullable=False)
    metodo_pagamento = Column(String, nullable=False)  # 'dinheiro', 'cartao', 'pix'
    status = Column(String, default="finalizada")  # 'finalizada', 'cancelada'

    # Relacionamentos
    usuario = relationship("User")
    itens = relationship("SaleItem", back_populates="venda")

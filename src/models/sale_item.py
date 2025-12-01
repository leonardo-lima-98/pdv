from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class SaleItem(Base):
    __tablename__ = "itens_venda"

    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Float, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Relacionamentos
    venda = relationship("Sale", back_populates="itens")
    produto = relationship("Product")

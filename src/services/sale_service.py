from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.sale import Sale
from ..models.sale_item import SaleItem
from ..models.product import Product
from ..schemas.sale import SaleCreate, SaleResponse, SaleSummary, SaleItemResponse
from typing import List, Optional
from datetime import datetime, date

def create_sale(db: Session, sale_data: SaleCreate, user_id: int) -> Sale:
    """Cria uma nova venda"""
    # Calcular total e validar estoque
    total = 0.0
    sale_items = []

    for item_data in sale_data.itens:
        product = db.query(Product).filter(Product.id == item_data.produto_id).first()
        if not product:
            raise ValueError(f"Produto {item_data.produto_id} não encontrado")

        if not product.ativo:
            raise ValueError(f"Produto {product.nome} está inativo")

        if product.estoque < item_data.quantidade:
            raise ValueError(f"Estoque insuficiente para {product.nome}. Disponível: {product.estoque}")

        subtotal = product.preco * item_data.quantidade
        total += subtotal

        sale_item = SaleItem(
            produto_id=item_data.produto_id,
            quantidade=item_data.quantidade,
            preco_unitario=product.preco,
            subtotal=subtotal
        )
        sale_items.append(sale_item)

    # Criar venda
    sale = Sale(
        usuario_id=user_id,
        total=total,
        metodo_pagamento=sale_data.metodo_pagamento
    )

    db.add(sale)
    db.flush()  # Para obter o ID da venda

    # Adicionar itens à venda
    for item in sale_items:
        item.venda_id = sale.id
        db.add(item)

        # Baixar estoque
        product = db.query(Product).filter(Product.id == item.produto_id).first()
        product.estoque -= item.quantidade

    db.commit()
    db.refresh(sale)
    return sale

def get_sale_by_id(db: Session, sale_id: int) -> Sale:
    """Busca venda por ID com itens"""
    return db.query(Sale).filter(Sale.id == sale_id).first()

def get_sales(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Sale]:
    """Lista vendas com filtros"""
    query = db.query(Sale)

    if user_id:
        query = query.filter(Sale.usuario_id == user_id)

    return query.order_by(Sale.data_hora.desc()).offset(skip).limit(limit).all()

def get_sales_by_date_range(db: Session, start_date: date, end_date: date) -> List[Sale]:
    """Busca vendas por período"""
    return db.query(Sale).filter(
        and_(
            Sale.data_hora >= start_date,
            Sale.data_hora <= end_date
        )
    ).all()

def format_sale_response(sale: Sale) -> SaleResponse:
    """Formata venda para resposta da API"""
    itens = []
    for item in sale.itens:
        itens.append(SaleItemResponse(
            id=item.id,
            produto_id=item.produto_id,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario,
            subtotal=item.subtotal,
            produto_nome=item.produto.nome
        ))

    return SaleResponse(
        id=sale.id,
        data_hora=sale.data_hora,
        usuario_id=sale.usuario_id,
        usuario_nome=sale.usuario.nome,
        total=sale.total,
        metodo_pagamento=sale.metodo_pagamento,
        status=sale.status,
        itens=itens
    )

def format_sale_summary(sale: Sale) -> SaleSummary:
    """Formata resumo da venda"""
    return SaleSummary(
        id=sale.id,
        data_hora=sale.data_hora,
        usuario_nome=sale.usuario.nome,
        total=sale.total,
        metodo_pagamento=sale.metodo_pagamento,
        status=sale.status
    )

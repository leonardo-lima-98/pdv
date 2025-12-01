from sqlalchemy.orm import Session
from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate, StockEntry
from typing import List

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """Lista todos os produtos ativos"""
    return db.query(Product).filter(Product.ativo == True).offset(skip).limit(limit).all()

def get_product_by_id(db: Session, product_id: int) -> Product:
    """Busca produto por ID"""
    return db.query(Product).filter(Product.id == product_id).first()

def get_product_by_barcode(db: Session, barcode: str) -> Product:
    """Busca produto por código de barras"""
    return db.query(Product).filter(Product.codigo_barras == barcode).first()

def create_product(db: Session, product_data: ProductCreate) -> Product:
    """Cria novo produto"""
    # Verificar se código de barras já existe (se fornecido)
    if product_data.codigo_barras:
        existing = db.query(Product).filter(Product.codigo_barras == product_data.codigo_barras).first()
        if existing:
            raise ValueError("Código de barras já cadastrado")

    product = Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Product:
    """Atualiza produto"""
    product = get_product_by_id(db, product_id)
    if not product:
        raise ValueError("Produto não encontrado")

    # Verificar código de barras único (se estiver sendo alterado)
    if product_data.codigo_barras is not None:
        existing = db.query(Product).filter(
            Product.codigo_barras == product_data.codigo_barras,
            Product.id != product_id
        ).first()
        if existing:
            raise ValueError("Código de barras já cadastrado")

    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: int) -> bool:
    """Desativa produto (soft delete)"""
    product = get_product_by_id(db, product_id)
    if not product:
        return False

    product.ativo = False
    db.commit()
    return True

def add_stock(db: Session, stock_entries: List[StockEntry]) -> List[Product]:
    """Adiciona estoque aos produtos"""
    updated_products = []

    for entry in stock_entries:
        product = get_product_by_id(db, entry.produto_id)
        if not product:
            raise ValueError(f"Produto {entry.produto_id} não encontrado")

        product.estoque += entry.quantidade
        updated_products.append(product)

    db.commit()
    # Refresh para obter dados atualizados
    for product in updated_products:
        db.refresh(product)

    return updated_products

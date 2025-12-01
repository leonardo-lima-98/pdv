from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services import (
    get_products, get_product_by_id, create_product, update_product,
    delete_product, add_stock
)
from ..schemas import ProductCreate, ProductUpdate, ProductResponse, StockEntry
from ..routes.auth import get_current_active_user, require_manager
from ..models import User

router = APIRouter(prefix="/produtos", tags=["produtos"])

@router.get("/", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista produtos ativos"""
    products = get_products(db, skip=skip, limit=limit)
    return products

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Busca produto por ID"""
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

@router.post("/", response_model=ProductResponse)
def create_new_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Cria novo produto (apenas gerente)"""
    try:
        product = create_product(db, product_data)
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{product_id}", response_model=ProductResponse)
def update_existing_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Atualiza produto (apenas gerente)"""
    try:
        product = update_product(db, product_id, product_data)
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{product_id}")
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Desativa produto (apenas gerente)"""
    success = delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return {"message": "Produto desativado com sucesso"}

@router.post("/estoque/entrada", response_model=List[ProductResponse])
def add_product_stock(
    stock_entries: List[StockEntry],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Adiciona estoque aos produtos (apenas gerente)"""
    try:
        updated_products = add_stock(db, stock_entries)
        return updated_products
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services import create_sale, get_sale_by_id, get_sales, format_sale_response, format_sale_summary
from ..schemas import SaleCreate, SaleResponse, SaleSummary
from ..routes.auth import get_current_active_user
from ..models import User

router = APIRouter(prefix="/vendas", tags=["vendas"])

@router.post("/", response_model=SaleResponse)
def create_new_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cria nova venda"""
    try:
        sale = create_sale(db, sale_data, current_user.id)
        return format_sale_response(sale)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[SaleSummary])
def list_sales(
    user_id: int = Query(None, description="Filtrar por usuário (opcional)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista vendas com filtros"""
    # Vendedor só vê suas próprias vendas, gerente vê todas
    if current_user.perfil == "vendedor":
        user_id = current_user.id

    sales = get_sales(db, user_id=user_id, skip=skip, limit=limit)
    return [format_sale_summary(sale) for sale in sales]

@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale_detail(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Busca detalhes da venda"""
    sale = get_sale_by_id(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Venda não encontrada")

    # Vendedor só vê suas próprias vendas
    if current_user.perfil == "vendedor" and sale.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    return format_sale_response(sale)

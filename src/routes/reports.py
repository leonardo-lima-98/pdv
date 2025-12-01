from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from ..database import get_db
from ..services import get_daily_sales_report, get_period_sales_report
from ..schemas import DailySalesReport, PeriodSalesReport
from ..routes.auth import get_current_active_user, require_manager
from ..models import User

router = APIRouter(prefix="/relatorios", tags=["relatórios"])

@router.get("/vendas-dia", response_model=DailySalesReport)
def get_daily_report(
    report_date: date = Query(None, description="Data do relatório (padrão: hoje)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Relatório de vendas do dia (apenas gerente)"""
    if report_date is None:
        report_date = date.today()

    return get_daily_sales_report(db, report_date)

@router.get("/vendas-periodo", response_model=PeriodSalesReport)
def get_period_report(
    start_date: date = Query(..., description="Data inicial"),
    end_date: date = Query(..., description="Data final"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Relatório de vendas por período (apenas gerente)"""
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Data inicial deve ser anterior à data final")

    # Limitar período para no máximo 90 dias
    delta = end_date - start_date
    if delta.days > 90:
        raise HTTPException(status_code=400, detail="Período máximo de 90 dias")

    return get_period_sales_report(db, start_date, end_date)

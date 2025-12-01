from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from ..models.sale import Sale
from ..models.sale_item import SaleItem
from ..schemas.report import DailySalesReport, PeriodSalesReport
from typing import Dict, List
from datetime import date, datetime
from collections import defaultdict

def get_daily_sales_report(db: Session, report_date: date) -> DailySalesReport:
    """Relatório de vendas do dia"""
    start_date = datetime.combine(report_date, datetime.min.time())
    end_date = datetime.combine(report_date, datetime.max.time())

    # Vendas do dia
    sales = db.query(Sale).filter(
        and_(
            Sale.data_hora >= start_date,
            Sale.data_hora <= end_date,
            Sale.status == "finalizada"
        )
    ).all()

    return _build_sales_report(sales, report_date)

def get_period_sales_report(db: Session, start_date: date, end_date: date) -> PeriodSalesReport:
    """Relatório de vendas por período"""
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    # Vendas do período
    sales = db.query(Sale).filter(
        and_(
            Sale.data_hora >= start_datetime,
            Sale.data_hora <= end_datetime,
            Sale.status == "finalizada"
        )
    ).all()

    report_data = _build_sales_report(sales)
    return PeriodSalesReport(
        **report_data.model_dump(),
        data_inicio=start_date,
        data_fim=end_date
    )

def _build_sales_report(sales: List[Sale], specific_date: date = None) -> DailySalesReport:
    """Constrói dados do relatório de vendas"""
    total_vendas = len(sales)
    valor_total = sum(sale.total for sale in sales)

    # Vendas por método de pagamento
    vendas_por_metodo = defaultdict(float)
    vendas_por_vendedor = defaultdict(lambda: {"total": 0.0, "vendas": 0})

    # Produtos mais vendidos
    produtos_vendidos = defaultdict(float)

    for sale in sales:
        # Método de pagamento
        vendas_por_metodo[sale.metodo_pagamento] += sale.total

        # Por vendedor
        vendedor_nome = sale.usuario.nome
        vendas_por_vendedor[vendedor_nome]["total"] += sale.total
        vendas_por_vendedor[vendedor_nome]["vendas"] += 1

        # Produtos vendidos
        for item in sale.itens:
            produtos_vendidos[item.produto.nome] += item.quantidade

    # Formatar vendas por método
    vendas_por_metodo_dict = dict(vendas_por_metodo)

    # Formatar vendas por vendedor
    vendas_por_vendedor_list = [
        {"vendedor": nome, "total": dados["total"], "vendas": dados["vendas"]}
        for nome, dados in vendas_por_vendedor.items()
    ]

    # Top produtos mais vendidos
    produtos_mais_vendidos = [
        {"produto": produto, "quantidade": quantidade}
        for produto, quantidade in sorted(produtos_vendidos.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    if specific_date:
        return DailySalesReport(
            data=specific_date,
            total_vendas=total_vendas,
            valor_total=valor_total,
            vendas_por_metodo=vendas_por_metodo_dict,
            produtos_mais_vendidos=produtos_mais_vendidos,
            vendas_por_vendedor=vendas_por_vendedor_list
        )
    else:
        return DailySalesReport(
            total_vendas=total_vendas,
            valor_total=valor_total,
            vendas_por_metodo=vendas_por_metodo_dict,
            produtos_mais_vendidos=produtos_mais_vendidos,
            vendas_por_vendedor=vendas_por_vendedor_list
        )

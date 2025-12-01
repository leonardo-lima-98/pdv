from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class SalesReport(BaseModel):
    total_vendas: int
    valor_total: float
    vendas_por_metodo: dict
    produtos_mais_vendidos: List[dict]
    vendas_por_vendedor: List[dict]

class DailySalesReport(SalesReport):
    data: date

class PeriodSalesReport(SalesReport):
    data_inicio: date
    data_fim: date

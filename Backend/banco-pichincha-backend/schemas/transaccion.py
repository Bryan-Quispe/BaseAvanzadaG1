# schemas/transaccion.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DepositoRequest(BaseModel):
    cuenta_id: str
    monto: float
    generar_recibo: bool
    cajero_id: Optional[str] = None

class RetiroTarjetaRequest(BaseModel):
    cuenta_id: str
    tarjeta_id: str
    monto: int
    generar_recibo: bool
    cajero_id: str

class ReciboResponse(BaseModel):
    transaccion_id: str
    cajero_id: str
    recibo_costo: float
    transaccion_fecha: datetime
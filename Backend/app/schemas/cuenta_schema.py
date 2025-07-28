from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal

class CuentaBase(BaseModel):
    """Esquema base para los datos de una cuenta."""
    id: str = Field(..., max_length=10, description="ID único de la cuenta, ej: '478758'")
    nombre: str = Field(..., max_length=64, description="Nombre de la cuenta, ej: 'Cuenta de Ahorros'")
    saldo: Decimal = Field(..., ge=0, description="Saldo inicial de la cuenta")
    estado: str = Field(..., max_length=32, description="Estado de la cuenta, ej: 'Activa'")
    limite_web: Decimal = Field(..., description="Límite para transacciones web")
    limite_movil: Decimal = Field(..., description="Límite para transacciones móviles")

class CuentaCrear(CuentaBase):
    """Esquema usado para crear una nueva cuenta."""
    pass

class CuentaLectura(CuentaBase):
    """Esquema para mostrar una cuenta en las respuestas de la API."""
    fecha_apertura: date

    class Config:
        from_attributes = True
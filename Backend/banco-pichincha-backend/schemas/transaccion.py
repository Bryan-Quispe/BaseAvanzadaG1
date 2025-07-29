# schemas/transaccion.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Esquemas para Cliente
class ClienteBase(BaseModel):
    cliente_id: str
    cliente_nombres: str
    cliente_apellidos: str
    cliente_correo: str
    cliente_celular: str
    cliente_direccion: str
    cliente_provincia: str
    cliente_ciudad: str
    cliente_fchnacimiento: datetime

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):
    cliente_nombres: Optional[str] = None
    cliente_apellidos: Optional[str] = None
    cliente_correo: Optional[str] = None
    cliente_celular: Optional[str] = None
    cliente_direccion: Optional[str] = None
    cliente_provincia: Optional[str] = None
    cliente_ciudad: Optional[str] = None
    cliente_fchnacimiento: Optional[datetime] = None

class ClienteResponse(ClienteBase):
    cuentas: List[str] = []  # Lista de IDs de cuentas asociadas

# Esquemas para Cuenta
class CuentaBase(BaseModel):
    cuenta_id: str
    cliente_id: str
    cuenta_nombre: str
    cuenta_saldo: float
    cuenta_apertura: datetime
    cuenta_estado: str
    cuenta_limite_trans_web: float
    cuenta_limite_trans_movil: float

class CuentaCreate(CuentaBase):
    pass

class CuentaUpdate(CuentaBase):
    cuenta_nombre: Optional[str] = None
    cuenta_saldo: Optional[float] = None
    cuenta_estado: Optional[str] = None
    cuenta_limite_trans_web: Optional[float] = None
    cuenta_limite_trans_movil: Optional[float] = None

class CuentaResponse(CuentaBase):
    pass

# Esquemas para Cajero
class CajeroBase(BaseModel):
    cajero_id: str
    cajero_ubicacion: str
    cajero_tipo: str
    cajero_estado: str

class CajeroCreate(CajeroBase):
    pass

class CajeroUpdate(CajeroBase):
    cajero_ubicacion: Optional[str] = None
    cajero_tipo: Optional[str] = None
    cajero_estado: Optional[str] = None

class CajeroResponse(CajeroBase):
    pass

# Esquemas para Transacciones
class DepositoRequest(BaseModel):
    cuenta_id: str
    monto: float
    generar_recibo: bool
    cajero_id: Optional[str] = None

class RetiroRequest(BaseModel):
    cuenta_id: str
    monto: int
    generar_recibo: bool
    cajero_id: str
    usar_tarjeta: bool = True
    tarjeta_id: Optional[str] = None

class ReciboResponse(BaseModel):
    transaccion_id: str
    cajero_id: str
    recibo_costo: float
    transaccion_fecha: datetime
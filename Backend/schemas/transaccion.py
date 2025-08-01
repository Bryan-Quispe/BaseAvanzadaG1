from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Esquemas para Cliente
class ClienteBase(BaseModel):
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
    cliente_id: str
    cliente_contrasena: Optional[str] = None
    cuentas: List[str] = []

# Esquemas para Cuenta
class CuentaBase(BaseModel):
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
    cliente_id: Optional[str] = None
    cuenta_nombre: Optional[str] = None
    cuenta_saldo: Optional[float] = None
    cuenta_estado: Optional[str] = None
    cuenta_limite_trans_web: Optional[float] = None
    cuenta_limite_trans_movil: Optional[float] = None

class CuentaResponse(CuentaBase):
    cuenta_id: str

# Esquemas para Cajero
class CajeroBase(BaseModel):
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
    cajero_id: str

# Esquemas para Tarjeta
class TarjetaBase(BaseModel):
    cuenta_id: str
    tarjeta_nombre: str
    tarjeta_pin_seguridad: str
    tarjeta_fecha_caducidad: datetime
    tarjeta_fecha_emision: datetime
    tarjeta_estado: str
    tarjeta_cvv: str
    tarjeta_estilo: str

class TarjetaCreate(TarjetaBase):
    pass

class TarjetaUpdate(TarjetaBase):
    cuenta_id: Optional[str] = None
    tarjeta_nombre: Optional[str] = None
    tarjeta_pin_seguridad: Optional[str] = None
    tarjeta_fecha_caducidad: Optional[datetime] = None
    tarjeta_fecha_emision: Optional[datetime] = None
    tarjeta_estado: Optional[str] = None
    tarjeta_cvv: Optional[str] = None
    tarjeta_estilo: Optional[str] = None

class TarjetaResponse(TarjetaBase):
    tarjeta_id: str

# Esquemas para Tarjeta de Crédito
class TarjetaCreditoBase(TarjetaBase):
    tarjetacredito_cupo: float
    tarjetacredito_pago_minimo: float
    tareja_credito_pago_total: float

class TarjetaCreditoCreate(TarjetaCreditoBase):
    pass

class TarjetaCreditoUpdate(TarjetaCreditoBase):
    cuenta_id: Optional[str] = None
    tarjeta_nombre: Optional[str] = None
    tarjeta_pin_seguridad: Optional[str] = None
    tarjeta_fecha_caducidad: Optional[datetime] = None
    tarjeta_fecha_emision: Optional[datetime] = None
    tarjeta_estado: Optional[str] = None
    tarjeta_cvv: Optional[str] = None
    tarjeta_estilo: Optional[str] = None
    tarjetacredito_cupo: Optional[float] = None
    tarjetacredito_pago_minimo: Optional[float] = None
    tareja_credito_pago_total: Optional[float] = None

class TarjetaCreditoResponse(TarjetaCreditoBase):
    tarjeta_id: str

# Esquemas para Tarjeta de Débito
class TarjetaDebitoBase(TarjetaBase):
    pass

class TarjetaDebitoCreate(TarjetaDebitoBase):
    pass

class TarjetaDebitoUpdate(TarjetaDebitoBase):
    cuenta_id: Optional[str] = None
    tarjeta_nombre: Optional[str] = None
    tarjeta_pin_seguridad: Optional[str] = None
    tarjeta_fecha_caducidad: Optional[datetime] = None
    tarjeta_fecha_emision: Optional[datetime] = None
    tarjeta_estado: Optional[str] = None
    tarjeta_cvv: Optional[str] = None
    tarjeta_estilo: Optional[str] = None

class TarjetaDebitoResponse(TarjetaDebitoBase):
    tarjeta_id: str

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
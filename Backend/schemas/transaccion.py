from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import datetime
import re
import pytz  # Importar pytz para manejar zonas horarias

# Esquemas para Cliente
class ClienteBase(BaseModel):
    cliente_nombres: str = Field(..., max_length=50, description="Nombres del cliente")
    cliente_apellidos: str = Field(..., max_length=50, description="Apellidos del cliente")
    cliente_correo: EmailStr = Field(..., description="Correo electrónico válido")
    cliente_celular: str = Field(..., max_length=10, description="Número de celular (10 dígitos)")
    cliente_direccion: str = Field(..., max_length=100, description="Dirección del cliente")
    cliente_provincia: str = Field(..., max_length=50, description="Provincia")
    cliente_ciudad: str = Field(..., max_length=50, description="Ciudad")
    cliente_fchnacimiento: datetime = Field(..., description="Fecha de nacimiento")

    @validator('cliente_celular')
    def validate_celular(cls, v):
        if not v.isdigit() or len(v) != 10 or not v.startswith('09'):
            raise ValueError('El celular debe ser un número de 10 dígitos que comience con 09')
        return v

    @validator('cliente_fchnacimiento')
    def validate_fecha_nacimiento(cls, v):
        # Hacer que today sea aware con UTC
        today = datetime.now(pytz.UTC)
        # Si v es aware, usarlo directamente; si es naive, asignarle UTC
        v_aware = v if v.tzinfo else v.replace(tzinfo=pytz.UTC)
        age = (today - v_aware).days // 365
        if age < 18:
            raise ValueError('El cliente debe ser mayor de 18 años')
        return v

class ClienteCreate(ClienteBase):
    cliente_id: str = Field(..., max_length=10, description="Cédula del cliente (10 dígitos)")

    @validator('cliente_id')
    def validate_cedula(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError('La cédula debe ser un string de 10 dígitos')
        # Opcional: Validación del dígito verificador de cédula ecuatoriana
        # coef = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        # suma = sum(int(v[i]) * coef[i] if int(v[i]) * coef[i] < 10 else int(v[i]) * coef[i] - 9 for i in range(9))
        # digito_verificador = (10 - (suma % 10)) % 10
        # if digito_verificador != int(v[9]):
        #     raise ValueError('Cédula inválida: dígito verificador incorrecto')
        return v

class ClienteUpdate(ClienteBase):
    cliente_nombres: Optional[str] = None
    cliente_apellidos: Optional[str] = None
    cliente_correo: Optional[EmailStr] = None
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
    cliente_id: str = Field(..., description="Cédula del cliente")
    cuenta_nombre: str = Field(..., max_length=50, description="Nombre de la cuenta")
    cuenta_saldo: float = Field(..., ge=0, description="Saldo de la cuenta (no negativo)")
    cuenta_apertura: datetime = Field(..., description="Fecha de apertura")
    cuenta_estado: str = Field(..., description="Estado de la cuenta (ACTIVA/INACTIVA)")
    cuenta_limite_trans_web: float = Field(..., ge=0, description="Límite de transacciones web")
    cuenta_limite_trans_movil: float = Field(..., ge=0, description="Límite de transacciones móviles")

    @validator('cuenta_estado')
    def validate_estado(cls, v):
        if v not in ['ACTIVA', 'INACTIVA']:
            raise ValueError('El estado debe ser ACTIVA o INACTIVA')
        return v

    @validator('cuenta_apertura')
    def validate_fecha_apertura(cls, v):
        # Asegurar que la fecha sea aware
        return v if v.tzinfo else v.replace(tzinfo=pytz.UTC)

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
    cajero_ubicacion: str = Field(..., max_length=100, description="Ubicación del cajero")
    cajero_tipo: str = Field(..., max_length=50, description="Tipo de cajero")
    cajero_estado: str = Field(..., description="Estado del cajero (ACTIVO/INACTIVO)")

    @validator('cajero_estado')
    def validate_estado(cls, v):
        if v not in ['ACTIVO', 'INACTIVO']:
            raise ValueError('El estado debe ser ACTIVO o INACTIVO')
        return v

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
    cuenta_id: str = Field(..., description="ID de la cuenta asociada")
    tarjeta_nombre: str = Field(..., max_length=50, description="Nombre en la tarjeta")
    tarjeta_pin_seguridad: str = Field(..., max_length=6, description="PIN de seguridad")
    tarjeta_fecha_caducidad: datetime = Field(..., description="Fecha de caducidad")
    tarjeta_fecha_emision: datetime = Field(..., description="Fecha de emisión")
    tarjeta_estado: str = Field(..., description="Estado de la tarjeta (ACTIVA/INACTIVA)")
    tarjeta_cvv: str = Field(..., max_length=3, description="CVV de la tarjeta")
    tarjeta_estilo: str = Field(..., max_length=50, description="Estilo de la tarjeta")

    @validator('tarjeta_pin_seguridad')
    def validate_pin(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('El PIN de seguridad debe ser un número de 6 dígitos')
        return v

    @validator('tarjeta_cvv')
    def validate_cvv(cls, v):
        if not v.isdigit() or len(v) != 3:
            raise ValueError('El CVV debe ser un número de 3 dígitos')
        return v

    @validator('tarjeta_estado')
    def validate_estado(cls, v):
        if v not in ['ACTIVA', 'INACTIVA']:
            raise ValueError('El estado debe ser ACTIVA o INACTIVA')
        return v

    @validator('tarjeta_fecha_caducidad', 'tarjeta_fecha_emision')
    def validate_fechas(cls, v):
        # Asegurar que las fechas sean aware
        return v if v.tzinfo else v.replace(tzinfo=pytz.UTC)

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
    tarjetacredito_cupo: float = Field(..., ge=0, description="Cupo de la tarjeta de crédito")
    tarjetacredito_pago_minimo: float = Field(..., ge=0, description="Pago mínimo")
    tarjeta_credito_pago_total: float = Field(..., ge=0, description="Pago total")

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
    tarjeta_credito_pago_total: Optional[float] = None

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
    cuenta_id: str = Field(..., description="ID de la cuenta")
    monto: float = Field(..., gt=0, description="Monto del depósito (positivo)")
    generar_recibo: bool = Field(..., description="Generar recibo")
    cajero_id: Optional[str] = None

class RetiroRequest(BaseModel):
    cuenta_id: str = Field(..., description="ID de la cuenta")
    monto: float = Field(..., gt=0, description="Monto del retiro (positivo)")
    generar_recibo: bool = Field(..., description="Generar recibo")
    cajero_id: str = Field(..., description="ID del cajero")
    usar_tarjeta: bool = Field(..., description="Usar tarjeta")
    tarjeta_id: Optional[str] = None

class ReciboResponse(BaseModel):
    transaccion_id: str
    cajero_id: str
    recibo_costo: float
    transaccion_fecha: datetime

    @validator('transaccion_fecha')
    def validate_transaccion_fecha(cls, v):
        
        return v if v.tzinfo else v.replace(tzinfo=pytz.UTC)
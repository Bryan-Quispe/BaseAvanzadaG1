from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import re
import pytz

# Esquemas para Cliente
class ClienteBase(BaseModel):
    cliente_nombres: str = Field(..., min_length=1, max_length=32, description="Nombres del cliente")
    cliente_apellidos: str = Field(..., min_length=1, max_length=32, description="Apellidos del cliente")
    cliente_correo: EmailStr = Field(..., max_length=64, description="Correo electrónico válido")
    cliente_celular: str = Field(..., min_length=10, max_length=10, description="Número de celular (10 dígitos)")
    cliente_direccion: str = Field(..., min_length=1, max_length=128, description="Dirección del cliente")
    cliente_provincia: str = Field(..., min_length=1, max_length=32, description="Provincia")
    cliente_ciudad: str = Field(..., min_length=1, max_length=32, description="Ciudad")
    cliente_fchnacimiento: date = Field(..., description="Fecha de nacimiento")

    @validator('cliente_celular')
    def validate_celular(cls, v):
        if not v.isdigit() or len(v) != 10 or not v.startswith('09'):
            raise ValueError('El celular debe ser un número de 10 dígitos que comience con 09')
        return v

    @validator('cliente_fchnacimiento')
    def validate_fecha_nacimiento(cls, v):
        today = datetime.now(pytz.UTC).date()
        age = (today - v).days // 365
        if age < 18:
            raise ValueError('El cliente debe ser mayor de 18 años')
        return v

class ClienteCreate(ClienteBase):
    cliente_id: str = Field(..., min_length=10, max_length=10, description="Cédula del cliente (10 dígitos)")
    cliente_contrasena: str = Field(..., min_length=6, description="Contraseña del cliente")

    @validator('cliente_id')
    def validate_cedula(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError('La cédula debe ser un string de 10 dígitos')
        coef = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = sum(int(v[i]) * coef[i] if int(v[i]) * coef[i] < 10 else int(v[i]) * coef[i] - 9 for i in range(9))
        digito_verificador = (10 - (suma % 10)) % 10
        if digito_verificador != int(v[9]):
            raise ValueError('Cédula inválida: dígito verificador incorrecto')
        return v

class ClienteUpdate(ClienteBase):
    cliente_nombres: Optional[str] = Field(None, min_length=1, max_length=32)
    cliente_apellidos: Optional[str] = Field(None, min_length=1, max_length=32)
    cliente_correo: Optional[EmailStr] = Field(None, max_length=64)
    cliente_celular: Optional[str] = Field(None, min_length=10, max_length=10)
    cliente_direccion: Optional[str] = Field(None, min_length=1, max_length=128)
    cliente_provincia: Optional[str] = Field(None, min_length=1, max_length=32)
    cliente_ciudad: Optional[str] = Field(None, min_length=1, max_length=32)
    cliente_fchnacimiento: Optional[date] = None

class ClienteResponse(ClienteBase):
    cliente_id: str
    cuentas: List[str] = []

    class Config:
        from_attributes = True

# Esquemas para Cuenta
class CuentaBase(BaseModel):
    cuenta_nombre: str = Field(..., min_length=1, max_length=64, description="Nombre de la cuenta")
    cuenta_saldo: Decimal = Field(..., ge=0, decimal_places=2, description="Saldo de la cuenta (no negativo)")
    cuenta_apertura: date = Field(..., description="Fecha de apertura")
    cuenta_estado: str = Field(..., min_length=1, max_length=32, description="Estado de la cuenta (ACTIVA/INACTIVA)")
    cuenta_limite_trans_web: Decimal = Field(..., ge=0, decimal_places=2, description="Límite de transacciones web")
    cuenta_limite_trans_movil: Decimal = Field(..., ge=0, decimal_places=2, description="Límite de transacciones móviles")

    @validator('cuenta_estado')
    def validate_estado(cls, v):
        if v not in ['ACTIVA', 'INACTIVA']:
            raise ValueError('El estado debe ser ACTIVA o INACTIVA')
        return v

class CuentaCreate(CuentaBase):
    cliente_id: str = Field(..., min_length=10, max_length=10, description="Cédula del cliente")

    @validator('cliente_id')
    def validate_cliente_id(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError('El cliente_id debe ser un string de 10 dígitos')
        return v

class CuentaUpdate(CuentaBase):
    cuenta_nombre: Optional[str] = Field(None, min_length=1, max_length=64)
    cuenta_saldo: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    cuenta_estado: Optional[str] = Field(None, min_length=1, max_length=32)
    cuenta_limite_trans_web: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    cuenta_limite_trans_movil: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

class CuentaResponse(CuentaBase):
    cuenta_id: str
    cliente_id: str

    class Config:
        from_attributes = True

# Esquemas para Cuenta Corriente (para manejar sobregiro)
class CuentaCorrienteCreate(CuentaCreate):
    cuentatrans_sobregiro: Optional[Decimal] = Field(None, ge=0, le=999.99, decimal_places=2, description="Límite de sobregiro (máximo 999.99)")

class CuentaCorrienteUpdate(CuentaUpdate):
    cuentatrans_sobregiro: Optional[Decimal] = Field(None, ge=0, le=999.99, decimal_places=2, description="Límite de sobregiro (máximo 999.99)")

class CuentaCorrienteResponse(CuentaResponse):
    cuentatrans_sobregiro: Optional[Decimal] = None

# Esquemas para Cajero
class CajeroBase(BaseModel):
    cajero_ubicacion: str = Field(..., min_length=1, max_length=128, description="Ubicación del cajero")
    cajero_tipo: str = Field(..., min_length=1, max_length=16, description="Tipo de cajero")
    cajero_estado: str = Field(..., min_length=1, max_length=16, description="Estado del cajero (ACTIVO/INACTIVO)")

    @validator('cajero_estado')
    def validate_estado(cls, v):
        if v not in ['ACTIVO', 'INACTIVO']:
            raise ValueError('El estado debe ser ACTIVO o INACTIVO')
        return v

class CajeroCreate(CajeroBase):
    pass

class CajeroUpdate(CajeroBase):
    cajero_ubicacion: Optional[str] = Field(None, min_length=1, max_length=128)
    cajero_tipo: Optional[str] = Field(None, min_length=1, max_length=16)
    cajero_estado: Optional[str] = Field(None, min_length=1, max_length=16)

class CajeroResponse(CajeroBase):
    cajero_id: str = Field(..., min_length=1, max_length=10)

    class Config:
        from_attributes = True

# Esquemas para Tarjeta
class TarjetaBase(BaseModel):
    cuenta_id: str = Field(..., min_length=1, max_length=10, description="ID de la cuenta asociada")
    tarjeta_nombre: str = Field(..., min_length=1, max_length=32, description="Nombre en la tarjeta")
    tarjeta_pin_seguridad: str = Field(..., min_length=6, max_length=6, description="PIN de seguridad (6 dígitos)")
    tarjeta_fecha_caducidad: date = Field(..., description="Fecha de caducidad")
    tarjeta_fecha_emision: date = Field(..., description="Fecha de emisión")
    tarjeta_estado: str = Field(..., min_length=1, max_length=16, description="Estado de la tarjeta (ACTIVA/INACTIVA)")
    tarjeta_cvv: str = Field(..., min_length=3, max_length=3, description="CVV de la tarjeta (3 dígitos)")
    tarjeta_estilo: str = Field(..., min_length=1, max_length=64, description="Estilo de la tarjeta")

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

    @validator('tarjeta_fecha_caducidad')
    def validate_fecha_caducidad(cls, v, values):
        today = datetime.now(pytz.UTC).date()
        if v < today:
            raise ValueError('La fecha de caducidad no puede estar en el pasado')
        if 'tarjeta_fecha_emision' in values and v <= values['tarjeta_fecha_emision']:
            raise ValueError('La fecha de caducidad debe ser posterior a la fecha de emisión')
        return v

class TarjetaCreate(TarjetaBase):
    pass

class TarjetaUpdate(TarjetaBase):
    cuenta_id: Optional[str] = Field(None, min_length=1, max_length=10)
    tarjeta_nombre: Optional[str] = Field(None, min_length=1, max_length=32)
    tarjeta_pin_seguridad: Optional[str] = Field(None, min_length=6, max_length=6)
    tarjeta_fecha_caducidad: Optional[date] = None
    tarjeta_fecha_emision: Optional[date] = None
    tarjeta_estado: Optional[str] = Field(None, min_length=1, max_length=16)
    tarjeta_cvv: Optional[str] = Field(None, min_length=3, max_length=3)
    tarjeta_estilo: Optional[str] = Field(None, min_length=1, max_length=64)

class TarjetaResponse(TarjetaBase):
    tarjeta_id: str = Field(..., min_length=1, max_length=16)

    class Config:
        from_attributes = True

# Esquemas para Tarjeta de Crédito
class TarjetaCreditoCreate(TarjetaBase):
    tarjetacredito_cupo: Decimal = Field(..., ge=0, le=999999.99, decimal_places=2, description="Cupo de la tarjeta de crédito (máximo 999999.99)")
    tarjetacredito_pago_minimo: Decimal = Field(..., ge=0, le=999999.99, decimal_places=2, description="Pago mínimo (máximo 999999.99)")
    tarjeta_credito_pago_total: Decimal = Field(..., ge=0, le=999999.99, decimal_places=2, description="Pago total (máximo 999999.99)")

class TarjetaCreditoUpdate(TarjetaBase):
    cuenta_id: Optional[str] = Field(None, min_length=1, max_length=10)
    tarjeta_nombre: Optional[str] = Field(None, min_length=1, max_length=32)
    tarjeta_pin_seguridad: Optional[str] = Field(None, min_length=6, max_length=6)
    tarjeta_fecha_caducidad: Optional[date] = None
    tarjeta_fecha_emision: Optional[date] = None
    tarjeta_estado: Optional[str] = Field(None, min_length=1, max_length=16)
    tarjeta_cvv: Optional[str] = Field(None, min_length=3, max_length=3)
    tarjeta_estilo: Optional[str] = Field(None, min_length=1, max_length=64)
    tarjetacredito_cupo: Optional[Decimal] = Field(None, ge=0, le=999999.99, decimal_places=2)
    tarjetacredito_pago_minimo: Optional[Decimal] = Field(None, ge=0, le=999999.99, decimal_places=2)
    tarjeta_credito_pago_total: Optional[Decimal] = Field(None, ge=0, le=999999.99, decimal_places=2)

class TarjetaCreditoResponse(TarjetaBase):
    tarjeta_id: str = Field(..., min_length=1, max_length=16)
    tarjetacredito_cupo: Decimal
    tarjetacredito_pago_minimo: Optional[Decimal] = None
    tarjeta_credito_pago_total: Optional[Decimal] = None

    class Config:
        from_attributes = True

# Esquemas para Tarjeta de Débito
class TarjetaDebitoCreate(TarjetaBase):
    pass

class TarjetaDebitoUpdate(TarjetaBase):
    cuenta_id: Optional[str] = Field(None, min_length=1, max_length=10)
    tarjeta_nombre: Optional[str] = Field(None, min_length=1, max_length=32)
    tarjeta_pin_seguridad: Optional[str] = Field(None, min_length=6, max_length=6)
    tarjeta_fecha_caducidad: Optional[date] = None
    tarjeta_fecha_emision: Optional[date] = None
    tarjeta_estado: Optional[str] = Field(None, min_length=1, max_length=16)
    tarjeta_cvv: Optional[str] = Field(None, min_length=3, max_length=3)
    tarjeta_estilo: Optional[str] = Field(None, min_length=1, max_length=64)

class TarjetaDebitoResponse(TarjetaBase):
    tarjeta_id: str = Field(..., min_length=1, max_length=16)

    class Config:
        from_attributes = True

# Esquemas para Transacciones
class DepositoRequest(BaseModel):
    cuenta_id: str = Field(..., min_length=1, max_length=10, description="ID de la cuenta")
    monto: Decimal = Field(..., gt=0, le=999999.99, decimal_places=2, description="Monto del depósito (positivo, máximo 999999.99)")
    generar_recibo: bool = Field(..., description="Generar recibo")
    cajero_id: Optional[str] = Field(None, min_length=1, max_length=10, description="ID del cajero")

class RetiroRequest(BaseModel):
    cuenta_id: str = Field(..., min_length=1, max_length=10, description="ID de la cuenta")
    monto: Decimal = Field(..., gt=0, le=1000, decimal_places=2, description="Monto del retiro (positivo, máximo 1000)")
    generar_recibo: bool = Field(..., description="Generar recibo")
    cajero_id: str = Field(..., min_length=1, max_length=10, description="ID del cajero")
    usar_tarjeta: bool = Field(..., description="Usar tarjeta")
    tarjeta_id: Optional[str] = Field(None, min_length=1, max_length=16, description="ID de la tarjeta")

    @validator('tarjeta_id')
    def validate_tarjeta_id(cls, v, values):
        if values.get('usar_tarjeta') and not v:
            raise ValueError('El tarjeta_id es obligatorio si usar_tarjeta es True')
        return v

class RetiroSinTarjetaRequest(BaseModel):
    cuenta_id: str = Field(..., min_length=1, max_length=10, description="ID de la cuenta desde la que se realiza el retiro")
    monto: Decimal = Field(..., ge=0.01, le=999999.99, decimal_places=2, description="Monto a retirar")
    descripcion: Optional[str] = Field(None, max_length=100, description="Descripción opcional del retiro")
    celular_beneficiario: str = Field(..., min_length=10, max_length=10, description="Número de celular del beneficiario (10 dígitos)")

    @validator('celular_beneficiario')
    def validate_celular_beneficiario(cls, v):
        if not v.isdigit() or len(v) != 10 or not v.startswith('09'):
            raise ValueError('El celular del beneficiario debe ser un número de 10 dígitos que comience con 09')
        return v

class RetiroSinTarjetaResponse(BaseModel):
    transaccion_id: str = Field(..., min_length=1, max_length=8, description="ID de la transacción")
    codigo_verificacion: str = Field(..., min_length=4, max_length=4, description="Código de verificación de 4 dígitos")

class ReciboResponse(BaseModel):
    transaccion_id: str = Field(..., min_length=1, max_length=8, description="ID de la transacción")
    cajero_id: str = Field(..., min_length=1, max_length=10, description="ID del cajero")
    recibo_costo: Decimal = Field(..., ge=0, le=999.99, decimal_places=2, description="Costo del recibo (máximo 999.99)")
    transaccion_fecha: datetime = Field(..., description="Fecha de la transacción")

    @validator('transaccion_fecha')
    def validate_transaccion_fecha(cls, v):
        return v if v.tzinfo else v.replace(tzinfo=pytz.UTC)

class TransaccionResponse(BaseModel):
    transaccion_id: str = Field(..., min_length=1, max_length=16, description="ID único de la transacción")
    cuenta_id: str = Field(..., min_length=1, max_length=10, description="ID de la cuenta asociada")
    transaccion_tipo: str = Field(..., min_length=1, max_length=32, description="Tipo de transacción (DEPOSITO, RETIRO, RETIRO_SIN_TARJETA, etc.)")
    transaccion_monto: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Monto de la transacción")
    transaccion_costo: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Costo de la transacción")
    transaccion_fecha: datetime = Field(..., description="Fecha y hora de la transacción")
    transaccion_descripcion: Optional[str] = Field(None, max_length=100, description="Descripción de la transacción")
    transaccion_recibo: Optional[int] = Field(None, description="ID del recibo asociado, si existe")

    class Config:
        from_attributes = True
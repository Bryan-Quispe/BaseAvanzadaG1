from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv
import uuid
from config.database import get_db
from schemas.transaccion import (
    ClienteCreate, ClienteUpdate, ClienteResponse,
    CuentaCreate, CuentaUpdate, CuentaResponse,
    CajeroCreate, CajeroUpdate, CajeroResponse,
    TarjetaCreate, TarjetaUpdate, TarjetaResponse,
    TarjetaCreditoCreate, TarjetaCreditoUpdate, TarjetaCreditoResponse,
    TarjetaDebitoCreate, TarjetaDebitoUpdate, TarjetaDebitoResponse,
    DepositoRequest, RetiroRequest, ReciboResponse
)
from sqlalchemy.sql import text
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación FastAPI
app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-frontend-domain.com"],  # Añade tu dominio de frontend en Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de JWT
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuración de encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelo para el cambio de contraseña
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=6, description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")

# Función para verificar la contraseña
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Función para obtener el hash de la contraseña
def get_password_hash(password):
    return pwd_context.hash(password)

# Función para crear un token de acceso
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Obtener usuario actual desde el token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        cliente_id: str = payload.get("sub")
        if cliente_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    cliente = db.execute(text("SELECT * FROM CLIENTE WHERE cliente_id = :cliente_id"), {"cliente_id": cliente_id}).fetchone()
    if cliente is None:
        raise credentials_exception
    return cliente

# Endpoint raíz
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Banco Pichincha"}

# Endpoint para autenticación
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    cliente = db.execute(text("SELECT * FROM CLIENTE WHERE cliente_id = :cliente_id"), {"cliente_id": form_data.username}).fetchone()
    if not cliente or not verify_password(form_data.password, cliente.cliente_contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": cliente.cliente_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para cambiar contraseña
@app.post("/clientes/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(request.current_password, current_user.cliente_contrasena):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    hashed_password = get_password_hash(request.new_password)
    db.execute(
        text("UPDATE CLIENTE SET cliente_contrasena = :contrasena WHERE cliente_id = :cliente_id"),
        {"contrasena": hashed_password, "cliente_id": current_user.cliente_id}
    )
    db.commit()
    return {"message": "Contraseña actualizada con éxito"}

# Endpoint para crear un cliente
@app.post("/clientes/", response_model=ClienteResponse)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    # Verificar si el cliente ya existe
    existing_cliente = db.execute(
        text("SELECT * FROM CLIENTE WHERE cliente_id = :cliente_id"),
        {"cliente_id": cliente.cliente_id}
    ).fetchone()
    if existing_cliente:
        raise HTTPException(status_code=400, detail="El cliente ya existe")
    
    # Crear hash de la contraseña por defecto (puedes personalizar esto)
    hashed_password = get_password_hash("default_password")  # Cambia esto según tus necesidades
    
    # Insertar cliente en la base de datos
    db.execute(
        text("""
            INSERT INTO CLIENTE (
                cliente_id, cliente_nombres, cliente_apellidos, cliente_correo,
                cliente_celular, cliente_direccion, cliente_provincia, cliente_ciudad,
                cliente_fchnacimiento, cliente_contrasena
            ) VALUES (
                :cliente_id, :cliente_nombres, :cliente_apellidos, :cliente_correo,
                :cliente_celular, :cliente_direccion, :cliente_provincia, :cliente_ciudad,
                :cliente_fchnacimiento, :cliente_contrasena
            )
        """),
        {
            "cliente_id": cliente.cliente_id,
            "cliente_nombres": cliente.cliente_nombres,
            "cliente_apellidos": cliente.cliente_apellidos,
            "cliente_correo": cliente.cliente_correo,
            "cliente_celular": cliente.cliente_celular,
            "cliente_direccion": cliente.cliente_direccion,
            "cliente_provincia": cliente.cliente_provincia,
            "cliente_ciudad": cliente.cliente_ciudad,
            "cliente_fchnacimiento": cliente.cliente_fchnacimiento,
            "cliente_contrasena": hashed_password
        }
    )
    db.commit()
    
    # Obtener el cliente creado
    cliente_data = db.execute(
        text("SELECT * FROM CLIENTE WHERE cliente_id = :cliente_id"),
        {"cliente_id": cliente.cliente_id}
    ).fetchone()
    
    return ClienteResponse(
        cliente_id=cliente_data.cliente_id,
        cliente_nombres=cliente_data.cliente_nombres,
        cliente_apellidos=cliente_data.cliente_apellidos,
        cliente_correo=cliente_data.cliente_correo,
        cliente_celular=cliente_data.cliente_celular,
        cliente_direccion=cliente_data.cliente_direccion,
        cliente_provincia=cliente_data.cliente_provincia,
        cliente_ciudad=cliente_data.cliente_ciudad,
        cliente_fchnacimiento=cliente_data.cliente_fchnacimiento
    )

# Nuevo endpoint: Obtener cliente por ID
@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
def get_cliente(cliente_id: str, db: Session = Depends(get_db)):
    cliente = db.execute(
        text("SELECT * FROM CLIENTE WHERE cliente_id = :cliente_id"),
        {"cliente_id": cliente_id}
    ).fetchone()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Obtener cuentas asociadas
    cuentas = db.execute(
        text("SELECT cuenta_id FROM CUENTA WHERE cliente_id = :cliente_id"),
        {"cliente_id": cliente_id}
    ).fetchall()
    cuentas_ids = [cuenta.cuenta_id for cuenta in cuentas]
    
    return ClienteResponse(
        cliente_id=cliente.cliente_id,
        cliente_nombres=cliente.cliente_nombres,
        cliente_apellidos=cliente.cliente_apellidos,
        cliente_correo=cliente.cliente_correo,
        cliente_celular=cliente.cliente_celular,
        cliente_direccion=cliente.cliente_direccion,
        cliente_provincia=cliente.cliente_provincia,
        cliente_ciudad=cliente.cliente_ciudad,
        cliente_fchnacimiento=cliente.cliente_fchnacimiento,
        cuentas=cuentas_ids
    )

# Nuevo endpoint: Obtener cuentas por cliente_id
@app.get("/clientes/{cliente_id}/cuentas", response_model=List[CuentaResponse])
def get_cuentas_by_cliente(cliente_id: str, db: Session = Depends(get_db)):
    cuentas = db.execute(
        text("""
            SELECT * FROM CUENTA WHERE cliente_id = :cliente_id
        """),
        {"cliente_id": cliente_id}
    ).fetchall()
    if not cuentas:
        return []
    
    return [
        CuentaResponse(
            cuenta_id=cuenta.cuenta_id,
            cliente_id=cuenta.cliente_id,
            cuenta_nombre=cuenta.cuenta_nombre,
            cuenta_saldo=cuenta.cuenta_saldo,
            cuenta_apertura=cuenta.cuenta_apertura,
            cuenta_estado=cuenta.cuenta_estado,
            cuenta_limite_trans_web=cuenta.cuenta_limite_trans_web,
            cuenta_limite_trans_movil=cuenta.cuenta_limite_trans_movil
        ) for cuenta in cuentas
    ]

# Nuevo endpoint: Obtener tarjetas por cuenta_id
@app.get("/cuentas/{cuenta_id}/tarjetas", response_model=List[TarjetaResponse])
def get_tarjetas_by_cuenta(cuenta_id: str, db: Session = Depends(get_db)):
    tarjetas = db.execute(
        text("""
            SELECT * FROM TARJETA WHERE cuenta_id = :cuenta_id
        """),
        {"cuenta_id": cuenta_id}
    ).fetchall()
    if not tarjetas:
        return []
    
    return [
        TarjetaResponse(
            tarjeta_id=tarjeta.tarjeta_id,
            cuenta_id=tarjeta.cuenta_id,
            tarjeta_nombre=tarjeta.tarjeta_nombre,
            tarjeta_pin_seguridad=tarjeta.tarjeta_pin_seguridad,
            tarjeta_fecha_caducidad=tarjeta.tarjeta_fecha_caducidad,
            tarjeta_fecha_emision=tarjeta.tarjeta_fecha_emision,
            tarjeta_estado=tarjeta.tarjeta_estado,
            tarjeta_cvv=tarjeta.tarjeta_cvv,
            tarjeta_estilo=tarjeta.tarjeta_estilo
        ) for tarjeta in tarjetas
    ]

# Nuevo endpoint: Obtener todos los cajeros
@app.get("/cajeros", response_model=List[CajeroResponse])
def get_cajeros(db: Session = Depends(get_db)):
    cajeros = db.execute(
        text("SELECT * FROM CAJERO")
    ).fetchall()
    if not cajeros:
        return []
    
    return [
        CajeroResponse(
            cajero_id=cajero.cajero_id,
            cajero_ubicacion=cajero.cajero_ubicacion,
            cajero_tipo=cajero.cajero_tipo,
            cajero_estado=cajero.cajero_estado
        ) for cajero in cajeros
    ]
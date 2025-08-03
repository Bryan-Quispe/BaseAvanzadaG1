from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os
import pytz
from dotenv import load_dotenv
from uuid import uuid4
from config.database import get_db
from schemas.transaccion import (
    ClienteCreate, ClienteUpdate, ClienteResponse,
    CuentaCreate, CuentaUpdate, CuentaResponse,
    CajeroCreate, CajeroUpdate, CajeroResponse,
    TarjetaCreate, TarjetaUpdate, TarjetaResponse,
    TarjetaCreditoCreate, TarjetaCreditoUpdate, TarjetaCreditoResponse,
    TarjetaDebitoCreate, TarjetaDebitoUpdate, TarjetaDebitoResponse,
    DepositoRequest, RetiroRequest, ReciboResponse,
    TransaccionResponse, RetiroSinTarjetaRequest
)
from sqlalchemy.sql import text
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación FastAPI
app = FastAPI(title="Banco Pichincha API")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de JWT y hashing
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")  # Cambiado a argon2 para evitar problemas con bcrypt

# Modelos
class Token(BaseModel):
    access_token: str
    token_type: str

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=6, description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")

# Autenticación
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        cliente_id: str = payload.get("sub")
        if cliente_id is None:
            raise credentials_exception
        query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
        result = db.execute(query, {"cliente_id": cliente_id})
        cliente = result.fetchone()
        if not cliente:
            raise credentials_exception
        return cliente_id
    except JWTError:
        raise credentials_exception

# Endpoint raíz
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Banco Pichincha"}

# Endpoint de login
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
    result = db.execute(query, {"cliente_id": form_data.username})
    cliente = result.fetchone()
    if not cliente or not pwd_context.verify(form_data.password, cliente.cliente_contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cédula o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": cliente.cliente_id, "exp": datetime.now(pytz.UTC) + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para cambiar contraseña
@app.post("/clientes/change-password/", response_model=dict)
async def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
        result = db.execute(query, {"cliente_id": cliente_id})
        cliente = result.fetchone()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        if not pwd_context.verify(request.current_password, cliente.cliente_contrasena):
            raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")
        
        hashed_password = pwd_context.hash(request.new_password)
        query = text("UPDATE CLIENTE SET cliente_contrasena = :password WHERE CLIENTE_ID = :cliente_id")
        db.execute(query, {"password": hashed_password, "cliente_id": cliente_id})
        db.commit()
        return {"message": "Contraseña cambiada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al cambiar contraseña: {str(e)}")

# CRUD para Cliente
@app.post("/clientes/", response_model=ClienteResponse)
async def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    try:
        query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
        result = db.execute(query, {"cliente_id": cliente.cliente_id})
        if result.fetchone():
            raise HTTPException(status_code=400, detail="La cédula ya está registrada")
        
        hashed_password = pwd_context.hash(cliente.cliente_contrasena)
        
        query = text("""
            INSERT INTO CLIENTE (
                CLIENTE_ID, CLIENTE_NOMBRES, CLIENTE_APELLIDOS, CLIENTE_CORREO,
                CLIENTE_CELULAR, CLIENTE_DIRECCION, CLIENTE_PROVINCIA,
                CLIENTE_CIUDAD, CLIENTE_FCHNACIMIENTO, CLIENTE_CONTRASENA
            ) VALUES (
                :cliente_id, :nombres, :apellidos, :correo, :celular,
                :direccion, :provincia, :ciudad, :fchnacimiento, :contrasena
            ) RETURNING CLIENTE_ID
        """)
        values = {
            "cliente_id": cliente.cliente_id,
            "nombres": cliente.cliente_nombres,
            "apellidos": cliente.cliente_apellidos,
            "correo": cliente.cliente_correo,
            "celular": cliente.cliente_celular,
            "direccion": cliente.cliente_direccion,
            "provincia": cliente.cliente_provincia,
            "ciudad": cliente.cliente_ciudad,
            "fchnacimiento": cliente.cliente_fchnacimiento,
            "contrasena": hashed_password
        }
        result = db.execute(query, values)
        cliente_id = result.fetchone().cliente_id
        db.commit()
        
        query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
        result = db.execute(query, {"cliente_id": cliente_id})
        cliente_db = result.fetchone()
        columns = result.keys()
        return ClienteResponse(
            cliente_id=cliente_db.cliente_id,
            cliente_nombres=cliente_db.cliente_nombres,
            cliente_apellidos=cliente_db.cliente_apellidos,
            cliente_correo=cliente_db.cliente_correo,
            cliente_celular=cliente_db.cliente_celular,
            cliente_direccion=cliente_db.cliente_direccion,
            cliente_provincia=cliente_db.cliente_provincia,
            cliente_ciudad=cliente_db.cliente_ciudad,
            cliente_fchnacimiento=cliente_db.cliente_fchnacimiento,
            cuentas=[]
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear cliente: {str(e)}")

@app.get("/clientes/", response_model=List[ClienteResponse])
async def leer_todos_clientes(db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
    result = db.execute(query, {"cliente_id": cliente_id})
    clientes = result.fetchall()
    if not clientes:
        raise HTTPException(status_code=404, detail="No se encontraron datos para este cliente")
    columns = result.keys()
    responses = []
    for cliente in clientes:
        cuentas = db.execute(
            text("SELECT cuenta_id FROM CUENTA WHERE cliente_id = :cliente_id"),
            {"cliente_id": cliente.cliente_id}
        ).fetchall()
        cuentas_ids = [cuenta.cuenta_id for cuenta in cuentas]
        responses.append(ClienteResponse(
            **{col: getattr(cliente, col) for col in columns},
            cuentas=cuentas_ids
        ))
    return responses

@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
async def leer_cliente(cliente_id: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if cliente_id != current_user:
        raise HTTPException(status_code=403, detail="No autorizado para ver los datos de otro cliente")
    query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
    result = db.execute(query, {"cliente_id": cliente_id})
    cliente = result.fetchone()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    columns = result.keys()
    cuentas = db.execute(
        text("SELECT cuenta_id FROM CUENTA WHERE cliente_id = :cliente_id"),
        {"cliente_id": cliente_id}
    ).fetchall()
    cuentas_ids = [cuenta.cuenta_id for cuenta in cuentas]
    return ClienteResponse(
        **{col: getattr(cliente, col) for col in columns},
        cuentas=cuentas_ids
    )

@app.put("/clientes/{cliente_id}", response_model=ClienteResponse)
async def actualizar_cliente(cliente_id: str, cliente: ClienteUpdate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        if cliente_id != current_user:
            raise HTTPException(status_code=403, detail="No autorizado para actualizar otro cliente")
        
        query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
        result = db.execute(query, {"cliente_id": cliente_id})
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        update_data = cliente.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        set_clause = ", ".join(f"{key.upper()} = :{key}" for key in update_data.keys())
        query = text(f"UPDATE CLIENTE SET {set_clause} WHERE CLIENTE_ID = :cliente_id")
        values = {**update_data, "cliente_id": cliente_id}
        db.execute(query, values)
        db.commit()
        
        query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
        result = db.execute(query, {"cliente_id": cliente_id})
        cliente_db = result.fetchone()
        columns = result.keys()
        cuentas = db.execute(
            text("SELECT cuenta_id FROM CUENTA WHERE cliente_id = :cliente_id"),
            {"cliente_id": cliente_id}
        ).fetchall()
        cuentas_ids = [cuenta.cuenta_id for cuenta in cuentas]
        return ClienteResponse(
            **{col: getattr(cliente_db, col) for col in columns},
            cuentas=cuentas_ids
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar cliente: {str(e)}")

@app.delete("/clientes/{cliente_id}")
async def eliminar_cliente(cliente_id: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        if cliente_id != current_user:
            raise HTTPException(status_code=403, detail="No autorizado para eliminar otro cliente")
        
        query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
        result = db.execute(query, {"cliente_id": cliente_id})
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        query = text("DELETE FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
        db.execute(query, {"cliente_id": cliente_id})
        db.commit()
        return {"message": "Cliente eliminado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar cliente: {str(e)}")

# CRUD para Cuenta
@app.post("/cuentas/", response_model=CuentaResponse)
async def crear_cuenta(cuenta: CuentaCreate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        if cuenta.cliente_id != cliente_id:
            raise HTTPException(status_code=403, detail="No autorizado para crear cuenta para otro cliente")
        
        query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
        result = db.execute(query, {"cliente_id": cuenta.cliente_id})
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        cuenta_id = str(uuid4())[:10]
        query = text("""
            INSERT INTO CUENTA (
                CUENTA_ID, CLIENTE_ID, CUENTA_NOMBRE, CUENTA_SALDO,
                CUENTA_APERTURA, CUENTA_ESTADO, CUENTA_LIMITE_TRANS_WEB,
                CUENTA_LIMITE_TRANS_MOVIL
            ) VALUES (
                :cuenta_id, :cliente_id, :nombre, :saldo, :apertura,
                :estado, :limite_web, :limite_movil
            ) RETURNING CUENTA_ID
        """)
        values = {
            "cuenta_id": cuenta_id,
            "cliente_id": cuenta.cliente_id,
            "nombre": cuenta.cuenta_nombre,
            "saldo": cuenta.cuenta_saldo,
            "apertura": cuenta.cuenta_apertura,
            "estado": cuenta.cuenta_estado,
            "limite_web": cuenta.cuenta_limite_trans_web,
            "limite_movil": cuenta.cuenta_limite_trans_movil
        }
        result = db.execute(query, values)
        cuenta_id = result.fetchone().cuenta_id
        db.commit()
        
        query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id")
        result = db.execute(query, {"cuenta_id": cuenta_id})
        cuenta_db = result.fetchone()
        columns = result.keys()
        return CuentaResponse(**{col: getattr(cuenta_db, col) for col in columns})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear cuenta: {str(e)}")

@app.get("/cuentas/{cuenta_id}", response_model=CuentaResponse)
async def leer_cuenta(cuenta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id")
    result = db.execute(query, {"cuenta_id": cuenta_id})
    cuenta = result.fetchone()
    if not cuenta or cuenta.cliente_id != cliente_id:
        raise HTTPException(status_code=403, detail="Cuenta no encontrada o no autorizada")
    columns = result.keys()
    return CuentaResponse(**{col: getattr(cuenta, col) for col in columns})

@app.get("/clientes/{cliente_id}/cuentas", response_model=List[CuentaResponse])
async def leer_cuentas_por_cliente(cliente_id: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if cliente_id != current_user:
        raise HTTPException(status_code=403, detail="No autorizado para ver cuentas de otro cliente")
    query = text("SELECT * FROM CUENTA WHERE CLIENTE_ID = :cliente_id")
    result = db.execute(query, {"cliente_id": cliente_id})
    cuentas = result.fetchall()
    if not cuentas:
        return []
    columns = result.keys()
    return [CuentaResponse(**{col: getattr(cuenta, col) for col in columns}) for cuenta in cuentas]

@app.put("/cuentas/{cuenta_id}", response_model=CuentaResponse)
async def actualizar_cuenta(cuenta_id: str, cuenta: CuentaUpdate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id")
        result = db.execute(query, {"cuenta_id": cuenta_id})
        cuenta_db = result.fetchone()
        if not cuenta_db:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        if cuenta_db.cliente_id != cliente_id:
            raise HTTPException(status_code=403, detail="No autorizado para actualizar esta cuenta")
        
        update_data = cuenta.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        if 'cliente_id' in update_data:
            raise HTTPException(status_code=400, detail="No se puede modificar el CLIENTE_ID")
        
        set_clause = ", ".join(f"{key.upper()} = :{key}" for key in update_data.keys())
        query = text(f"UPDATE CUENTA SET {set_clause} WHERE CUENTA_ID = :cuenta_id")
        values = {**update_data, "cuenta_id": cuenta_id}
        db.execute(query, values)
        db.commit()
        
        query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id")
        result = db.execute(query, {"cuenta_id": cuenta_id})
        cuenta_db = result.fetchone()
        columns = result.keys()
        return CuentaResponse(**{col: getattr(cuenta_db, col) for col in columns})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar cuenta: {str(e)}")

@app.delete("/cuentas/{cuenta_id}")
async def eliminar_cuenta(cuenta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id")
        result = db.execute(query, {"cuenta_id": cuenta_id})
        cuenta = result.fetchone()
        if not cuenta:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        if cuenta.cliente_id != cliente_id:
            raise HTTPException(status_code=403, detail="No autorizado para eliminar esta cuenta")
        
        query = text("DELETE FROM CUENTA WHERE CUENTA_ID = :cuenta_id")
        db.execute(query, {"cuenta_id": cuenta_id})
        db.commit()
        return {"message": "Cuenta eliminada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar cuenta: {str(e)}")

# CRUD para Cajero
@app.post("/cajeros/", response_model=CajeroResponse)
async def crear_cajero(cajero: CajeroCreate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        cajero_id = str(uuid4())[:10]
        query = text("""
            INSERT INTO CAJERO (
                CAJERO_ID, CAJERO_UBICACION, CAJERO_TIPO, CAJERO_ESTADO
            ) VALUES (
                :cajero_id, :ubicacion, :tipo, :estado
            ) RETURNING CAJERO_ID
        """)
        values = {
            "cajero_id": cajero_id,
            "ubicacion": cajero.cajero_ubicacion,
            "tipo": cajero.cajero_tipo,
            "estado": cajero.cajero_estado
        }
        result = db.execute(query, values)
        cajero_id = result.fetchone().cajero_id
        db.commit()
        
        query = text("SELECT * FROM CAJERO WHERE CAJERO_ID = :cajero_id")
        result = db.execute(query, {"cajero_id": cajero_id})
        cajero_db = result.fetchone()
        columns = result.keys()
        return CajeroResponse(**{col: getattr(cajero_db, col) for col in columns})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear cajero: {str(e)}")

@app.get("/cajeros/", response_model=List[CajeroResponse])
async def leer_todos_cajeros(db: Session = Depends(get_db)):
    query = text("SELECT * FROM CAJERO")
    result = db.execute(query)
    cajeros = result.fetchall()
    if not cajeros:
        return []
    columns = result.keys()
    return [CajeroResponse(**{col: getattr(cajero, col) for col in columns}) for cajero in cajeros]

@app.get("/cajeros/{cajero_id}", response_model=CajeroResponse)
async def leer_cajero(cajero_id: str, db: Session = Depends(get_db)):
    query = text("SELECT * FROM CAJERO WHERE CAJERO_ID = :cajero_id")
    result = db.execute(query, {"cajero_id": cajero_id})
    cajero = result.fetchone()
    if not cajero:
        raise HTTPException(status_code=404, detail="Cajero no encontrado")
    columns = result.keys()
    return CajeroResponse(**{col: getattr(cajero, col) for col in columns})

@app.put("/cajeros/{cajero_id}", response_model=CajeroResponse)
async def actualizar_cajero(cajero_id: str, cajero: CajeroUpdate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("SELECT * FROM CAJERO WHERE CAJERO_ID = :cajero_id")
        result = db.execute(query, {"cajero_id": cajero_id})
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="Cajero no encontrado")
        
        update_data = cajero.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        set_clause = ", ".join(f"{key.upper()} = :{key}" for key in update_data.keys())
        query = text(f"UPDATE CAJERO SET {set_clause} WHERE CAJERO_ID = :cajero_id")
        values = {**update_data, "cajero_id": cajero_id}
        db.execute(query, values)
        db.commit()
        
        query = text("SELECT * FROM CAJERO WHERE CAJERO_ID = :cajero_id")
        result = db.execute(query, {"cajero_id": cajero_id})
        cajero_db = result.fetchone()
        columns = result.keys()
        return CajeroResponse(**{col: getattr(cajero_db, col) for col in columns})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar cajero: {str(e)}")

@app.delete("/cajeros/{cajero_id}")
async def eliminar_cajero(cajero_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("SELECT * FROM CAJERO WHERE CAJERO_ID = :cajero_id")
        result = db.execute(query, {"cajero_id": cajero_id})
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="Cajero no encontrado")
        
        query = text("DELETE FROM CAJERO WHERE CAJERO_ID = :cajero_id")
        db.execute(query, {"cajero_id": cajero_id})
        db.commit()
        return {"message": "Cajero eliminado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar cajero: {str(e)}")

# CRUD para Tarjeta
@app.post("/tarjetas/", response_model=TarjetaResponse)
async def crear_tarjeta(tarjeta: TarjetaCreate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id")
        result = db.execute(query, {"cuenta_id": tarjeta.cuenta_id})
        cuenta = result.fetchone()
        if not cuenta:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        if cuenta.cliente_id != cliente_id:
            raise HTTPException(status_code=403, detail="No autorizado para crear tarjeta para esta cuenta")
        
        tarjeta_id = str(uuid4())[:16]
        query = text("""
            INSERT INTO TARJETA (
                TARJETA_ID, CUENTA_ID, TARJETA_NOMBRE, TARJETA_PIN_SEGURIDAD,
                TARJETA_FECHA_CADUCIDAD, TARJETA_FECHA_EMISION, TARJETA_ESTADO,
                TARJETA_CVV, TARJETA_ESTILO
            ) VALUES (
                :tarjeta_id, :cuenta_id, :nombre, :pin_seguridad, :fecha_caducidad,
                :fecha_emision, :estado, :cvv, :estilo
            ) RETURNING TARJETA_ID
        """)
        values = {
            "tarjeta_id": tarjeta_id,
            "cuenta_id": tarjeta.cuenta_id,
            "nombre": tarjeta.tarjeta_nombre,
            "pin_seguridad": tarjeta.tarjeta_pin_seguridad,
            "fecha_caducidad": tarjeta.tarjeta_fecha_caducidad,
            "fecha_emision": tarjeta.tarjeta_fecha_emision,
            "estado": tarjeta.tarjeta_estado,
            "cvv": tarjeta.tarjeta_cvv,
            "estilo": tarjeta.tarjeta_estilo
        }
        result = db.execute(query, values)
        tarjeta_id = result.fetchone().tarjeta_id
        db.commit()
        
        query = text("SELECT * FROM TARJETA WHERE TARJETA_ID = :tarjeta_id")
        result = db.execute(query, {"tarjeta_id": tarjeta_id})
        tarjeta_db = result.fetchone()
        columns = result.keys()
        return TarjetaResponse(**{col: getattr(tarjeta_db, col) for col in columns})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear tarjeta: {str(e)}")

@app.get("/cuentas/{cuenta_id}/tarjetas", response_model=List[TarjetaResponse])
async def leer_tarjetas_por_cuenta(cuenta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    query = text("""
        SELECT t.* FROM TARJETA t
        JOIN CUENTA c ON t.CUENTA_ID = c.CUENTA_ID
        WHERE t.CUENTA_ID = :cuenta_id AND c.CLIENTE_ID = :cliente_id
    """)
    result = db.execute(query, {"cuenta_id": cuenta_id, "cliente_id": cliente_id})
    tarjetas = result.fetchall()
    if not tarjetas:
        return []
    columns = result.keys()
    return [TarjetaResponse(**{col: getattr(tarjeta, col) for col in columns}) for tarjeta in tarjetas]

@app.get("/tarjetas/{tarjeta_id}", response_model=TarjetaResponse)
async def leer_tarjeta(tarjeta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    query = text("""
        SELECT t.* FROM TARJETA t
        JOIN CUENTA c ON t.CUENTA_ID = c.CUENTA_ID
        WHERE t.TARJETA_ID = :tarjeta_id AND c.CLIENTE_ID = :cliente_id
    """)
    result = db.execute(query, {"tarjeta_id": tarjeta_id, "cliente_id": cliente_id})
    tarjeta = result.fetchone()
    if not tarjeta:
        raise HTTPException(status_code=403, detail="Tarjeta no encontrada o no autorizada")
    columns = result.keys()
    return TarjetaResponse(**{col: getattr(tarjeta, col) for col in columns})

@app.put("/tarjetas/{tarjeta_id}", response_model=TarjetaResponse)
async def actualizar_tarjeta(tarjeta_id: str, tarjeta: TarjetaUpdate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("""
            SELECT t.* FROM TARJETA t
            JOIN CUENTA c ON t.CUENTA_ID = c.CUENTA_ID
            WHERE t.TARJETA_ID = :tarjeta_id AND c.CLIENTE_ID = :cliente_id
        """)
        result = db.execute(query, {"tarjeta_id": tarjeta_id, "cliente_id": cliente_id})
        tarjeta_db = result.fetchone()
        if not tarjeta_db:
            raise HTTPException(status_code=404, detail="Tarjeta no encontrada o no autorizada")
        
        update_data = tarjeta.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        set_clause = ", ".join(f"{key.upper()} = :{key}" for key in update_data.keys())
        query = text(f"UPDATE TARJETA SET {set_clause} WHERE TARJETA_ID = :tarjeta_id")
        values = {**update_data, "tarjeta_id": tarjeta_id}
        db.execute(query, values)
        db.commit()
        
        query = text("SELECT * FROM TARJETA WHERE TARJETA_ID = :tarjeta_id")
        result = db.execute(query, {"tarjeta_id": tarjeta_id})
        tarjeta_db = result.fetchone()
        columns = result.keys()
        return TarjetaResponse(**{col: getattr(tarjeta_db, col) for col in columns})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar tarjeta: {str(e)}")

@app.delete("/tarjetas/{tarjeta_id}")
async def eliminar_tarjeta(tarjeta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("""
            SELECT t.* FROM TARJETA t
            JOIN CUENTA c ON t.CUENTA_ID = c.CUENTA_ID
            WHERE t.TARJETA_ID = :tarjeta_id AND c.CLIENTE_ID = :cliente_id
        """)
        result = db.execute(query, {"tarjeta_id": tarjeta_id, "cliente_id": cliente_id})
        tarjeta = result.fetchone()
        if not tarjeta:
            raise HTTPException(status_code=404, detail="Tarjeta no encontrada o no autorizada")
        
        query = text("DELETE FROM TARJETA WHERE TARJETA_ID = :tarjeta_id")
        db.execute(query, {"tarjeta_id": tarjeta_id})
        db.commit()
        return {"message": "Tarjeta eliminada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar tarjeta: {str(e)}")

# CRUD para Tarjeta de Crédito
@app.post("/tarjetas-credito/", response_model=TarjetaCreditoResponse)
async def crear_tarjeta_credito(tarjeta: TarjetaCreditoCreate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id")
        result = db.execute(query, {"cuenta_id": tarjeta.cuenta_id})
        cuenta = result.fetchone()
        if not cuenta:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        if cuenta.cliente_id != cliente_id:
            raise HTTPException(status_code=403, detail="No autorizado para crear tarjeta de crédito para esta cuenta")
        
        tarjeta_id = str(uuid4())[:16]
        query = text("""
            INSERT INTO TARJETA_DE_CREDITO (
                TARJETA_ID, CUENTA_ID, TARJETA_NOMBRE, TARJETA_PIN_SEGURIDAD,
                TARJETA_FECHA_CADUCIDAD, TARJETA_FECHA_EMISION, TARJETA_ESTADO,
                TARJETA_CVV, TARJETA_ESTILO, TARJETACREDITO_CUPO,
                TARJETA_CREDITO_PAGO_MINIMO, TARJETA_CREDITO_PAGO_TOTAL
            ) VALUES (
                :tarjeta_id, :cuenta_id, :nombre, :pin_seguridad, :fecha_caducidad,
                :fecha_emision, :estado, :cvv, :estilo, :cupo, :pago_minimo, :pago_total
            ) RETURNING TARJETA_ID
        """)
        values = {
            "tarjeta_id": tarjeta_id,
            "cuenta_id": tarjeta.cuenta_id,
            "nombre": tarjeta.tarjeta_nombre,
            "pin_seguridad": tarjeta.tarjeta_pin_seguridad,
            "fecha_caducidad": tarjeta.tarjeta_fecha_caducidad,
            "fecha_emision": tarjeta.tarjeta_fecha_emision,
            "estado": tarjeta.tarjeta_estado,
            "cvv": tarjeta.tarjeta_cvv,
            "estilo": tarjeta.tarjeta_estilo,
            "cupo": tarjeta.tarjetacredito_cupo,
            "pago_minimo": tarjeta.tarjetacredito_pago_minimo,
            "pago_total": tarjeta.tarjeta_credito_pago_total
        }
        result = db.execute(query, values)
        tarjeta_id = result.fetchone().tarjeta_id
        db.commit()
        
        query = text("""
            SELECT 
                TARJETA_ID AS tarjeta_id,
                CUENTA_ID AS cuenta_id,
                TARJETA_NOMBRE AS tarjeta_nombre,
                TARJETA_PIN_SEGURIDAD AS tarjeta_pin_seguridad,
                TARJETA_FECHA_CADUCIDAD AS tarjeta_fecha_caducidad,
                TARJETA_FECHA_EMISION AS tarjeta_fecha_emision,
                TARJETA_ESTADO AS tarjeta_estado,
                TARJETA_CVV AS tarjeta_cvv,
                TARJETA_ESTILO AS tarjeta_estilo,
                TARJETACREDITO_CUPO AS tarjetacredito_cupo,
                TARJETA_CREDITO_PAGO_MINIMO AS tarjetacredito_pago_minimo,
                TARJETA_CREDITO_PAGO_TOTAL AS tarjeta_credito_pago_total
            FROM TARJETA_DE_CREDITO 
            WHERE TARJETA_ID = :tarjeta_id
        """)
        result = db.execute(query, {"tarjeta_id": tarjeta_id})
        tarjeta_db = result.fetchone()
        columns = result.keys()
        return TarjetaCreditoResponse(**{col: getattr(tarjeta_db, col) for col in columns})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear tarjeta de crédito: {str(e)}")

@app.get("/cuentas/{cuenta_id}/tarjetas-credito", response_model=List[TarjetaCreditoResponse])
async def leer_tarjetas_credito_por_cuenta(cuenta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    query = text("""
        SELECT 
            tc.TARJETA_ID AS tarjeta_id,
            tc.CUENTA_ID AS cuenta_id,
            tc.TARJETA_NOMBRE AS tarjeta_nombre,
            tc.TARJETA_PIN_SEGURIDAD AS tarjeta_pin_seguridad,
            tc.TARJETA_FECHA_CADUCIDAD AS tarjeta_fecha_caducidad,
            tc.TARJETA_FECHA_EMISION AS tarjeta_fecha_emision,
            tc.TARJETA_ESTADO AS tarjeta_estado,
            tc.TARJETA_CVV AS tarjeta_cvv,
            tc.TARJETA_ESTILO AS tarjeta_estilo,
            tc.TARJETACREDITO_CUPO AS tarjetacredito_cupo,
            tc.TARJETA_CREDITO_PAGO_MINIMO AS tarjetacredito_pago_minimo,
            tc.TARJETA_CREDITO_PAGO_TOTAL AS tarjeta_credito_pago_total
        FROM TARJETA_DE_CREDITO tc
        JOIN CUENTA c ON tc.CUENTA_ID = c.CUENTA_ID
        WHERE tc.CUENTA_ID = :cuenta_id AND c.CLIENTE_ID = :cliente_id
    """)
    result = db.execute(query, {"cuenta_id": cuenta_id, "cliente_id": cliente_id})
    tarjetas = result.fetchall()
    if not tarjetas:
        return []
    columns = result.keys()
    return [TarjetaCreditoResponse(**{col: getattr(tarjeta, col) for col in columns}) for tarjeta in tarjetas]

@app.get("/tarjetas-credito/{tarjeta_id}", response_model=TarjetaCreditoResponse)
async def leer_tarjeta_credito(tarjeta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    query = text("""
        SELECT 
            tc.TARJETA_ID AS tarjeta_id,
            tc.CUENTA_ID AS cuenta_id,
            tc.TARJETA_NOMBRE AS tarjeta_nombre,
            tc.TARJETA_PIN_SEGURIDAD AS tarjeta_pin_seguridad,
            tc.TARJETA_FECHA_CADUCIDAD AS tarjeta_fecha_caducidad,
            tc.TARJETA_FECHA_EMISION AS tarjeta_fecha_emision,
            tc.TARJETA_ESTADO AS tarjeta_estado,
            tc.TARJETA_CVV AS tarjeta_cvv,
            tc.TARJETA_ESTILO AS tarjeta_estilo,
            tc.TARJETACREDITO_CUPO AS tarjetacredito_cupo,
            tc.TARJETA_CREDITO_PAGO_MINIMO AS tarjetacredito_pago_minimo,
            tc.TARJETA_CREDITO_PAGO_TOTAL AS tarjeta_credito_pago_total
        FROM TARJETA_DE_CREDITO tc
        JOIN CUENTA c ON tc.CUENTA_ID = c.CUENTA_ID
        WHERE tc.TARJETA_ID = :tarjeta_id AND c.CLIENTE_ID = :cliente_id
    """)
    result = db.execute(query, {"tarjeta_id": tarjeta_id, "cliente_id": cliente_id})
    tarjeta = result.fetchone()
    if not tarjeta:
        raise HTTPException(status_code=403, detail="Tarjeta de crédito no encontrada o no autorizada")
    columns = result.keys()
    return TarjetaCreditoResponse(**{col: getattr(tarjeta, col) for col in columns})

@app.put("/tarjetas-credito/{tarjeta_id}", response_model=TarjetaCreditoResponse)
async def actualizar_tarjeta_credito(tarjeta_id: str, tarjeta: TarjetaCreditoUpdate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("""
            SELECT 
                tc.TARJETA_ID AS tarjeta_id,
                tc.CUENTA_ID AS cuenta_id,
                tc.TARJETA_NOMBRE AS tarjeta_nombre,
                tc.TARJETA_PIN_SEGURIDAD AS tarjeta_pin_seguridad,
                tc.TARJETA_FECHA_CADUCIDAD AS tarjeta_fecha_caducidad,
                tc.TARJETA_FECHA_EMISION AS tarjeta_fecha_emision,
                tc.TARJETA_ESTADO AS tarjeta_estado,
                tc.TARJETA_CVV AS tarjeta_cvv,
                tc.TARJETA_ESTILO AS tarjeta_estilo,
                tc.TARJETACREDITO_CUPO AS tarjetacredito_cupo,
                tc.TARJETA_CREDITO_PAGO_MINIMO AS tarjetacredito_pago_minimo,
                tc.TARJETA_CREDITO_PAGO_TOTAL AS tarjeta_credito_pago_total
            FROM TARJETA_DE_CREDITO tc
            JOIN CUENTA c ON tc.CUENTA_ID = c.CUENTA_ID
            WHERE tc.TARJETA_ID = :tarjeta_id AND c.CLIENTE_ID = :cliente_id
        """)
        result = db.execute(query, {"tarjeta_id": tarjeta_id, "cliente_id": cliente_id})
        tarjeta_db = result.fetchone()
        if not tarjeta_db:
            raise HTTPException(status_code=404, detail="Tarjeta de crédito no encontrada o no autorizada")
        
        update_data = tarjeta.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        column_mapping = {
            "tarjeta_id": "TARJETA_ID",
            "cuenta_id": "CUENTA_ID",
            "tarjeta_nombre": "TARJETA_NOMBRE",
            "tarjeta_pin_seguridad": "TARJETA_PIN_SEGURIDAD",
            "tarjeta_fecha_caducidad": "TARJETA_FECHA_CADUCIDAD",
            "tarjeta_fecha_emision": "TARJETA_FECHA_EMISION",
            "tarjeta_estado": "TARJETA_ESTADO",
            "tarjeta_cvv": "TARJETA_CVV",
            "tarjeta_estilo": "TARJETA_ESTILO",
            "tarjetacredito_cupo": "TARJETACREDITO_CUPO",
            "tarjetacredito_pago_minimo": "TARJETA_CREDITO_PAGO_MINIMO",
            "tarjeta_credito_pago_total": "TARJETA_CREDITO_PAGO_TOTAL"
        }
        set_clause = ", ".join(f"{column_mapping[key]} = :{key}" for key in update_data.keys())
        query = text(f"UPDATE TARJETA_DE_CREDITO SET {set_clause} WHERE TARJETA_ID = :tarjeta_id")
        values = {**update_data, "tarjeta_id": tarjeta_id}
        db.execute(query, values)
        db.commit()
        
        query = text("""
            SELECT 
                TARJETA_ID AS tarjeta_id,
                CUENTA_ID AS cuenta_id,
                TARJETA_NOMBRE AS tarjeta_nombre,
                TARJETA_PIN_SEGURIDAD AS tarjeta_pin_seguridad,
                TARJETA_FECHA_CADUCIDAD AS tarjeta_fecha_caducidad,
                TARJETA_FECHA_EMISION AS tarjeta_fecha_emision,
                TARJETA_ESTADO AS tarjeta_estado,
                TARJETA_CVV AS tarjeta_cvv,
                TARJETA_ESTILO AS tarjeta_estilo,
                TARJETACREDITO_CUPO AS tarjetacredito_cupo,
                TARJETA_CREDITO_PAGO_MINIMO AS tarjetacredito_pago_minimo,
                TARJETA_CREDITO_PAGO_TOTAL AS tarjeta_credito_pago_total
            FROM TARJETA_DE_CREDITO 
            WHERE TARJETA_ID = :tarjeta_id
        """)
        result = db.execute(query, {"tarjeta_id": tarjeta_id})
        tarjeta_db = result.fetchone()
        columns = result.keys()
        return TarjetaCreditoResponse(**{col: getattr(tarjeta_db, col) for col in columns})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar tarjeta de crédito: {str(e)}")

@app.delete("/tarjetas-credito/{tarjeta_id}")
async def eliminar_tarjeta_credito(tarjeta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("""
            SELECT tc.* FROM TARJETA_DE_CREDITO tc
            JOIN CUENTA c ON tc.CUENTA_ID = c.CUENTA_ID
            WHERE tc.TARJETA_ID = :tarjeta_id AND c.CLIENTE_ID = :cliente_id
        """)
        result = db.execute(query, {"tarjeta_id": tarjeta_id, "cliente_id": cliente_id})
        tarjeta = result.fetchone()
        if not tarjeta:
            raise HTTPException(status_code=404, detail="Tarjeta de crédito no encontrada o no autorizada")
        
        query = text("DELETE FROM TARJETA_DE_CREDITO WHERE TARJETA_ID = :tarjeta_id")
        db.execute(query, {"tarjeta_id": tarjeta_id})
        db.commit()
        return {"message": "Tarjeta de crédito eliminada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar tarjeta de crédito: {str(e)}")

# CRUD para Tarjeta de Débito
@app.post("/tarjetas-debito/", response_model=TarjetaDebitoResponse)
async def crear_tarjeta_debito(tarjeta: TarjetaDebitoCreate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id")
        result = db.execute(query, {"cuenta_id": tarjeta.cuenta_id})
        cuenta = result.fetchone()
        if not cuenta:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        if cuenta.cliente_id != cliente_id:
            raise HTTPException(status_code=403, detail="No autorizado para crear tarjeta de débito para esta cuenta")
        
        tarjeta_id = str(uuid4())[:16]
        query = text("""
            INSERT INTO TARJETA_DE_DEBITO (
                TARJETA_ID, CUENTA_ID, TARJETA_NOMBRE, TARJETA_PIN_SEGURIDAD,
                TARJETA_FECHA_CADUCIDAD, TARJETA_FECHA_EMISION, TARJETA_ESTADO,
                TARJETA_CVV, TARJETA_ESTILO
            ) VALUES (
                :tarjeta_id, :cuenta_id, :nombre, :pin_seguridad, :fecha_caducidad,
                :fecha_emision, :estado, :cvv, :estilo
            ) RETURNING TARJETA_ID
        """)
        values = {
            "tarjeta_id": tarjeta_id,
            "cuenta_id": tarjeta.cuenta_id,
            "nombre": tarjeta.tarjeta_nombre,
            "pin_seguridad": tarjeta.tarjeta_pin_seguridad,
            "fecha_caducidad": tarjeta.tarjeta_fecha_caducidad,
            "fecha_emision": tarjeta.tarjeta_fecha_emision,
            "estado": tarjeta.tarjeta_estado,
            "cvv": tarjeta.tarjeta_cvv,
            "estilo": tarjeta.tarjeta_estilo
        }
        result = db.execute(query, values)
        tarjeta_id = result.fetchone().tarjeta_id
        db.commit()
        
        query = text("SELECT * FROM TARJETA_DE_DEBITO WHERE TARJETA_ID = :tarjeta_id")
        result = db.execute(query, {"tarjeta_id": tarjeta_id})
        tarjeta_db = result.fetchone()
        columns = result.keys()
        return TarjetaDebitoResponse(**{col: getattr(tarjeta_db, col) for col in columns})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear tarjeta de débito: {str(e)}")

@app.get("/cuentas/{cuenta_id}/tarjetas-debito", response_model=List[TarjetaDebitoResponse], description="Obtiene todas las tarjetas de débito asociadas a una cuenta específica.")
async def leer_tarjetas_debito_por_cuenta(cuenta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    query = text("""
        SELECT td.* FROM TARJETA_DE_DEBITO td
        JOIN CUENTA c ON td.CUENTA_ID = c.CUENTA_ID
        WHERE td.CUENTA_ID = :cuenta_id AND c.CLIENTE_ID = :cliente_id
    """)
    result = db.execute(query, {"cuenta_id": cuenta_id, "cliente_id": cliente_id})
    tarjetas = result.fetchall()
    if not tarjetas:
        return []
    columns = result.keys()
    return [TarjetaDebitoResponse(**{col: getattr(tarjeta, col) for col in columns}) for tarjeta in tarjetas]

@app.get("/tarjetas-debito/{tarjeta_id}", response_model=TarjetaDebitoResponse)
async def leer_tarjeta_debito(tarjeta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    query = text("""
        SELECT td.* FROM TARJETA_DE_DEBITO td
        JOIN CUENTA c ON td.CUENTA_ID = c.CUENTA_ID
        WHERE td.TARJETA_ID = :tarjeta_id AND c.CLIENTE_ID = :cliente_id
    """)
    result = db.execute(query, {"tarjeta_id": tarjeta_id, "cliente_id": cliente_id})
    tarjeta = result.fetchone()
    if not tarjeta:
        raise HTTPException(status_code=403, detail="Tarjeta de débito no encontrada o no autorizada")
    columns = result.keys()
    return TarjetaDebitoResponse(**{col: getattr(tarjeta, col) for col in columns})

@app.put("/tarjetas-debito/{tarjeta_id}", response_model=TarjetaDebitoResponse)
async def actualizar_tarjeta_debito(tarjeta_id: str, tarjeta: TarjetaDebitoUpdate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("""
            SELECT td.* FROM TARJETA_DE_DEBITO td
            JOIN CUENTA c ON td.CUENTA_ID = c.CUENTA_ID
            WHERE td.TARJETA_ID = :tarjeta_id AND c.CLIENTE_ID = :cliente_id
        """)
        result = db.execute(query, {"tarjeta_id": tarjeta_id, "cliente_id": cliente_id})
        tarjeta_db = result.fetchone()
        if not tarjeta_db:
            raise HTTPException(status_code=404, detail="Tarjeta de débito no encontrada o no autorizada")
        
        update_data = tarjeta.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        set_clause = ", ".join(f"{key.upper()} = :{key}" for key in update_data.keys())
        query = text(f"UPDATE TARJETA_DE_DEBITO SET {set_clause} WHERE TARJETA_ID = :tarjeta_id")
        values = {**update_data, "tarjeta_id": tarjeta_id}
        db.execute(query, values)
        db.commit()
        
        query = text("SELECT * FROM TARJETA_DE_DEBITO WHERE TARJETA_ID = :tarjeta_id")
        result = db.execute(query, {"tarjeta_id": tarjeta_id})
        tarjeta_db = result.fetchone()
        columns = result.keys()
        return TarjetaDebitoResponse(**{col: getattr(tarjeta_db, col) for col in columns})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar tarjeta de débito: {str(e)}")

@app.delete("/tarjetas-debito/{tarjeta_id}")
async def eliminar_tarjeta_debito(tarjeta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("""
            SELECT td.* FROM TARJETA_DE_DEBITO td
            JOIN CUENTA c ON td.CUENTA_ID = c.CUENTA_ID
            WHERE td.TARJETA_ID = :tarjeta_id AND c.CLIENTE_ID = :cliente_id
        """)
        result = db.execute(query, {"tarjeta_id": tarjeta_id, "cliente_id": cliente_id})
        tarjeta = result.fetchone()
        if not tarjeta:
            raise HTTPException(status_code=404, detail="Tarjeta de débito no encontrada o no autorizada")
        
        query = text("DELETE FROM TARJETA_DE_DEBITO WHERE TARJETA_ID = :tarjeta_id")
        db.execute(query, {"tarjeta_id": tarjeta_id})
        db.commit()
        return {"message": "Tarjeta de débito eliminada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar tarjeta de débito: {str(e)}")

# Endpoint para depósito
@app.post("/transacciones/deposito", response_model=dict)
async def deposito(deposito: DepositoRequest, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id AND CUENTA_ESTADO = :estado")
        result = db.execute(query, {"cuenta_id": deposito.cuenta_id, "estado": "ACTIVA"})
        cuenta = result.fetchone()
        if not cuenta or cuenta.cliente_id != cliente_id:
            raise HTTPException(status_code=403, detail="Acceso no autorizado a esta cuenta")
        
        if deposito.monto > cuenta.cuenta_limite_trans_web:
            raise HTTPException(status_code=400, detail="El monto excede el límite de transacciones web")
        
        if deposito.cajero_id:
            query = text("SELECT * FROM CAJERO WHERE CAJERO_ID = :cajero_id AND CAJERO_ESTADO = :estado")
            result = db.execute(query, {"cajero_id": deposito.cajero_id, "estado": "ACTIVO"})
            if not result.fetchone():
                raise HTTPException(status_code=404, detail="Cajero no encontrado o inactivo")
        
        transaccion_id = str(uuid4())[:8].upper()
        transaccion_costo = 0.50
        transaccion_fecha = datetime.now(pytz.UTC)
        
        query = text("""
            INSERT INTO TRANSACCION (
                TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO
            ) VALUES (
                :transaccion_id, :cuenta_id, :costo, :fecha, :recibo
            ) RETURNING TRANSACCION_ID
        """)
        result = db.execute(query, {
            "transaccion_id": transaccion_id,
            "cuenta_id": deposito.cuenta_id,
            "costo": transaccion_costo,
            "fecha": transaccion_fecha,
            "recibo": 1 if deposito.generar_recibo else None
        })
        transaccion_id = result.fetchone().transaccion_id
        
        query = text("""
            INSERT INTO DEPOSITO (
                TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO
            ) VALUES (
                :transaccion_id, :cuenta_id, :costo, :fecha, :recibo
            )
        """)
        db.execute(query, {
            "transaccion_id": transaccion_id,
            "cuenta_id": deposito.cuenta_id,
            "costo": transaccion_costo,
            "fecha": transaccion_fecha,
            "recibo": 1 if deposito.generar_recibo else None
        })
        
        query = text("UPDATE CUENTA SET CUENTA_SALDO = CUENTA_SALDO + :monto WHERE CUENTA_ID = :cuenta_id")
        db.execute(query, {"monto": deposito.monto, "cuenta_id": deposito.cuenta_id})
        
        recibo = None
        if deposito.generar_recibo and deposito.cajero_id:
            recibo_costo = 0.25
            query = text("INSERT INTO RECIBO (TRANSACCION_ID, CAJERO_ID, RECIBO_COSTO) VALUES (:transaccion_id, :cajero_id, :costo)")
            db.execute(query, {"transaccion_id": transaccion_id, "cajero_id": deposito.cajero_id, "costo": recibo_costo})
            recibo = ReciboResponse(
                transaccion_id=transaccion_id,
                cajero_id=deposito.cajero_id,
                recibo_costo=recibo_costo,
                transaccion_fecha=transaccion_fecha
            )
        
        db.commit()
        return {"transaccion_id": transaccion_id, "recibo": recibo.dict() if recibo else None}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en depósito: {str(e)}")

# Endpoint para retiro
@app.post("/transacciones/retiro", response_model=dict)
async def retiro(retiro: RetiroRequest, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id AND CUENTA_ESTADO = :estado")
        result = db.execute(query, {"cuenta_id": retiro.cuenta_id, "estado": "ACTIVA"})
        cuenta = result.fetchone()
        if not cuenta or cuenta.cliente_id != cliente_id:
            raise HTTPException(status_code=403, detail="Acceso no autorizado a esta cuenta")
        if cuenta.cuenta_saldo < retiro.monto:
            raise HTTPException(status_code=400, detail="Saldo insuficiente")
        
        query = text("SELECT * FROM CAJERO WHERE CAJERO_ID = :cajero_id AND CAJERO_ESTADO = :estado")
        result = db.execute(query, {"cajero_id": retiro.cajero_id, "estado": "ACTIVO"})
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="Cajero no encontrado o inactivo")
        
        if retiro.monto > cuenta.cuenta_limite_trans_movil and retiro.usar_tarjeta:
            raise HTTPException(status_code=400, detail="El monto excede el límite de transacciones móviles")
        
        transaccion_id = str(uuid4())[:8].upper()
        transaccion_costo = 1.00 if retiro.usar_tarjeta else 0.75
        transaccion_fecha = datetime.now(pytz.UTC)
        
        query = text("""
            INSERT INTO TRANSACCION (
                TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO
            ) VALUES (
                :transaccion_id, :cuenta_id, :costo, :fecha, :recibo
            ) RETURNING TRANSACCION_ID
        """)
        result = db.execute(query, {
            "transaccion_id": transaccion_id,
            "cuenta_id": retiro.cuenta_id,
            "costo": transaccion_costo,
            "fecha": transaccion_fecha,
            "recibo": 1 if retiro.generar_recibo else None
        })
        transaccion_id = result.fetchone().transaccion_id
        
        query = text("""
            INSERT INTO RETIRO (
                TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA,
                TRANSACCION_RECIBO, RETIRO_MONTO, RETIRO_MONTO_MAX
            ) VALUES (
                :transaccion_id, :cuenta_id, :costo, :fecha, :recibo, :monto, :monto_max
            )
        """)
        db.execute(query, {
            "transaccion_id": transaccion_id,
            "cuenta_id": retiro.cuenta_id,
            "costo": transaccion_costo,
            "fecha": transaccion_fecha,
            "recibo": 1 if retiro.generar_recibo else None,
            "monto": retiro.monto,
            "monto_max": 1000
        })
        
        if retiro.usar_tarjeta and retiro.tarjeta_id:
            query = text("SELECT * FROM TARJETA WHERE TARJETA_ID = :tarjeta_id AND CUENTA_ID = :cuenta_id AND TARJETA_ESTADO = :estado")
            result = db.execute(query, {"tarjeta_id": retiro.tarjeta_id, "cuenta_id": retiro.cuenta_id, "estado": "ACTIVA"})
            tarjeta = result.fetchone()
            if not tarjeta:
                raise HTTPException(status_code=404, detail="Tarjeta no encontrada o inactiva")
            query = text("""
                INSERT INTO RETIRO_CON_TARJETA (
                    TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA,
                    TRANSACCION_RECIBO, RETIRO_MONTO, RETIRO_MONTO_MAX, RETIROCT_TARJETA,
                    RETIROCT_AID, RETIROCT_P22, RETIROCT_P38, RETIROCT_COSTO_INTERBANCARIO
                ) VALUES (
                    :transaccion_id, :cuenta_id, :costo, :fecha, :recibo, :monto,
                    :monto_max, :tarjeta, :aid, :p22, :p38, :costo_inter
                )
            """)
            db.execute(query, {
                "transaccion_id": transaccion_id,
                "cuenta_id": retiro.cuenta_id,
                "costo": transaccion_costo,
                "fecha": transaccion_fecha,
                "recibo": 1 if retiro.generar_recibo else None,
                "monto": retiro.monto,
                "monto_max": 1000,
                "tarjeta": retiro.tarjeta_id,
                "aid": "A0000000041010",
                "p22": "123",
                "p38": "123456",
                "costo_inter": 0.10
            })
        else:
            query = text("""
                INSERT INTO RETIRO_SIN_TARJETA (
                    TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA,
                    TRANSACCION_RECIBO, RETIRO_MONTO, RETIRO_MONTO_MAX,
                    RETIROST_CELULAR_BENEFICIARIO, RETIROST_CLAVE,
                    RETIROST_DURACION, RETIROST_MAXIMO_RETIROS
                ) VALUES (
                    :transaccion_id, :cuenta_id, :costo, :fecha, :recibo, :monto,
                    :monto_max, :celular_beneficiario, :clave, :duracion, :maximo_retiros
                )
            """)
            db.execute(query, {
                "transaccion_id": transaccion_id,
                "cuenta_id": retiro.cuenta_id,
                "costo": transaccion_costo,
                "fecha": transaccion_fecha,
                "recibo": 1 if retiro.generar_recibo else None,
                "monto": retiro.monto,
                "monto_max": 1000,
                "celular_beneficiario": "0999999999",
                "clave": "1234",
                "duracion": 24,
                "maximo_retiros": 1
            })
        
        query = text("UPDATE CUENTA SET CUENTA_SALDO = CUENTA_SALDO - :monto WHERE CUENTA_ID = :cuenta_id")
        db.execute(query, {"monto": retiro.monto, "cuenta_id": retiro.cuenta_id})
        
        recibo = None
        if retiro.generar_recibo and retiro.cajero_id:
            recibo_costo = 0.25
            query = text("INSERT INTO RECIBO (TRANSACCION_ID, CAJERO_ID, RECIBO_COSTO) VALUES (:transaccion_id, :cajero_id, :costo)")
            db.execute(query, {"transaccion_id": transaccion_id, "cajero_id": retiro.cajero_id, "costo": recibo_costo})
            recibo = ReciboResponse(
                transaccion_id=transaccion_id,
                cajero_id=retiro.cajero_id,
                recibo_costo=recibo_costo,
                transaccion_fecha=transaccion_fecha
            )
        
        db.commit()
        return {"transaccion_id": transaccion_id, "recibo": recibo.dict() if recibo else None}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en retiro: {str(e)}")

# Endpoint para retiro sin tarjeta
@app.post(
    "/cuentas/{cuenta_id}/retiro-sin-tarjeta",
    response_model=TransaccionResponse,
    description="Realiza un retiro sin tarjeta desde una cuenta específica."
)
async def retiro_sin_tarjeta(
    cuenta_id: str,
    retiro: RetiroSinTarjetaRequest,
    db: Session = Depends(get_db),
    cliente_id: str = Depends(get_current_user)
):
    try:
        # Verificar que la cuenta existe y pertenece al cliente
        query_cuenta = text("""
            SELECT CUENTA_ID, CUENTA_SALDO 
            FROM CUENTA 
            WHERE CUENTA_ID = :cuenta_id AND CLIENTE_ID = :cliente_id
        """)
        result_cuenta = db.execute(query_cuenta, {"cuenta_id": cuenta_id, "cliente_id": cliente_id}).fetchone()
        if not result_cuenta:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada o no pertenece al cliente")

        saldo_actual = result_cuenta.CUENTA_SALDO
        if saldo_actual < retiro.monto:
            raise HTTPException(status_code=400, detail="Saldo insuficiente para el retiro")

        # Actualizar el saldo de la cuenta
        nuevo_saldo = saldo_actual - retiro.monto
        query_actualizar_saldo = text("""
            UPDATE CUENTA 
            SET CUENTA_SALDO = :nuevo_saldo 
            WHERE CUENTA_ID = :cuenta_id
        """)
        db.execute(query_actualizar_saldo, {"nuevo_saldo": nuevo_saldo, "cuenta_id": cuenta_id})

        # Registrar la transacción
        transaccion_id = str(uuid4())[:16]
        query_insertar_transaccion = text("""
            INSERT INTO TRANSACCION (
                TRANSACCION_ID, 
                CUENTA_ID, 
                TRANSACCION_TIPO, 
                TRANSACCION_MONTO, 
                TRANSACCION_FECHA, 
                TRANSACCION_DESCRIPCION
            )
            VALUES (
                :transaccion_id, 
                :cuenta_id, 
                :transaccion_tipo, 
                :transaccion_monto, 
                :transaccion_fecha, 
                :transaccion_descripcion
            )
            RETURNING *
        """)
        result_transaccion = db.execute(query_insertar_transaccion, {
            "transaccion_id": transaccion_id,
            "cuenta_id": cuenta_id,
            "transaccion_tipo": "RETIRO_SIN_TARJETA",
            "transaccion_monto": retiro.monto,
            "transaccion_fecha": datetime.now(pytz.UTC),
            "transaccion_descripcion": retiro.descripcion or "Retiro sin tarjeta"
        }).fetchone()
        db.commit()

        columns = result_transaccion._mapping.keys()
        return TransaccionResponse(**{col: getattr(result_transaccion, col) for col in columns})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al realizar el retiro: {str(e)}")

# Endpoint para obtener transacciones por cuenta
@app.get(
    "/cuentas/{cuenta_id}/transacciones",
    response_model=List[TransaccionResponse],
    description="Obtiene todas las transacciones asociadas a una cuenta específica."
)
async def leer_transacciones_por_cuenta(
    cuenta_id: str,
    db: Session = Depends(get_db),
    cliente_id: str = Depends(get_current_user)
):
    try:
        query = text("""
            SELECT t.* 
            FROM TRANSACCION t
            JOIN CUENTA c ON t.CUENTA_ID = c.CUENTA_ID
            WHERE t.CUENTA_ID = :cuenta_id AND c.CLIENTE_ID = :cliente_id
        """)
        result = db.execute(query, {"cuenta_id": cuenta_id, "cliente_id": cliente_id})
        transacciones = result.fetchall()
        if not transacciones:
            return []
        columns = result.keys()
        return [TransaccionResponse(**{col: getattr(transaccion, col) for col in columns}) for transaccion in transacciones]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener transacciones: {str(e)}")
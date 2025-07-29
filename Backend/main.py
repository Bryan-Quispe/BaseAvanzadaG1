from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv
import uuid
from config.database import get_db
from schemas.transaccion import ClienteCreate, ClienteUpdate, ClienteResponse, CuentaCreate, CuentaUpdate, CuentaResponse, CajeroCreate, CajeroUpdate, CajeroResponse, DepositoRequest, RetiroRequest, ReciboResponse
from sqlalchemy.sql import text
from passlib.context import CryptContext

load_dotenv()

app = FastAPI(title="Banco Pichincha API")

# Configuración de JWT y hashing
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token válido por 30 minutos
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# Modelos
class Token(BaseModel):
    access_token: str
    token_type: str

class SetPasswordRequest(BaseModel):
    cliente_id: str
    password: str

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
        {"sub": cliente.cliente_id, "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para establecer contraseña inicial
@app.post("/clientes/set-password/")
async def set_initial_password(request: SetPasswordRequest, db: Session = Depends(get_db)):
    query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
    result = db.execute(query, {"cliente_id": request.cliente_id})
    cliente = result.fetchone()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    hashed_password = pwd_context.hash(request.password)
    query = text("UPDATE CLIENTE SET cliente_contrasena = :password WHERE CLIENTE_ID = :cliente_id")
    db.execute(query, {"password": hashed_password, "cliente_id": request.cliente_id})
    db.commit()
    return {"message": "Contraseña establecida correctamente"}

# CRUD para Cliente
@app.post("/clientes/", response_model=ClienteResponse)
async def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    # Lógica para crear cliente (vacía por ahora, añadiría hashed_password si se pasa)
    pass

@app.get("/clientes/", response_model=List[ClienteResponse])
async def leer_todos_clientes(db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    query = text("SELECT * FROM CLIENTE")
    result = db.execute(query)
    clientes = result.fetchall()
    if not clientes:
        raise HTTPException(status_code=404, detail="No se encontraron clientes")
    columns = result.keys()
    return [ClienteResponse(**{col: getattr(cliente, col) for col in columns}) for cliente in clientes]

@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
async def leer_cliente(cliente_id: str, db: Session = Depends(get_db)):
    query = text("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id")
    result = db.execute(query, {"cliente_id": cliente_id})
    cliente = result.fetchone()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    columns = result.keys()
    return ClienteResponse(**{col: getattr(cliente, col) for col in columns})

@app.put("/clientes/{cliente_id}", response_model=ClienteResponse)
async def actualizar_cliente(cliente_id: str, cliente: ClienteUpdate, db: Session = Depends(get_db)):
    # Lógica para actualizar cliente (vacía por ahora)
    pass

@app.delete("/clientes/{cliente_id}")
async def eliminar_cliente(cliente_id: str, db: Session = Depends(get_db)):
    # Lógica para eliminar cliente (vacía por ahora)
    pass

# CRUD para Cuenta
@app.post("/cuentas/", response_model=CuentaResponse)
async def crear_cuenta(cuenta: CuentaCreate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    # Lógica para crear cuenta (vacía por ahora)
    pass

@app.get("/cuentas/{cuenta_id}", response_model=CuentaResponse)
async def leer_cuenta(cuenta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id")
    result = db.execute(query, {"cuenta_id": cuenta_id})
    cuenta = result.fetchone()
    if not cuenta or cuenta.CLIENTE_ID != cliente_id:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada o no autorizada")
    columns = result.keys()
    return CuentaResponse(**{col: getattr(cuenta, col) for col in columns})

@app.put("/cuentas/{cuenta_id}", response_model=CuentaResponse)
async def actualizar_cuenta(cuenta_id: str, cuenta: CuentaUpdate, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    # Lógica para actualizar cuenta (vacía por ahora)
    pass

@app.delete("/cuentas/{cuenta_id}")
async def eliminar_cuenta(cuenta_id: str, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    # Lógica para eliminar cuenta (vacía por ahora)
    pass

# CRUD para Cajero
@app.post("/cajeros/", response_model=CajeroResponse)
async def crear_cajero(cajero: CajeroCreate, db: Session = Depends(get_db)):
    # Lógica para crear cajero (vacía por ahora)
    pass

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
async def actualizar_cajero(cajero_id: str, cajero: CajeroUpdate, db: Session = Depends(get_db)):
    # Lógica para actualizar cajero (vacía por ahora)
    pass

@app.delete("/cajeros/{cajero_id}")
async def eliminar_cajero(cajero_id: str, db: Session = Depends(get_db)):
    # Lógica para eliminar cajero (vacía por ahora)
    pass

# Endpoint para depósito
@app.post("/transacciones/deposito", response_model=dict)
async def deposito(deposito: DepositoRequest, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        query = text("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id AND CUENTA_ESTADO = :estado")
        result = db.execute(query, {"cuenta_id": deposito.cuenta_id, "estado": "ACTIVA"})
        cuenta = result.fetchone()
        if not cuenta or cuenta.CLIENTE_ID != cliente_id:
            raise HTTPException(status_code=403, detail="Acceso no autorizado a esta cuenta")
        transaccion_id = str(uuid.uuid4())[:8].upper()
        transaccion_costo = 0.50
        transaccion_fecha = datetime.now()
        query = text(
            "INSERT INTO TRANSACCION (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO) "
            "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo)"
        )
        db.execute(query, {"transaccion_id": transaccion_id, "cuenta_id": deposito.cuenta_id, "costo": transaccion_costo, "fecha": transaccion_fecha, "recibo": 1 if deposito.generar_recibo else None})
        query = text(
            "INSERT INTO DEPOSITO (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO) "
            "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo)"
        )
        db.execute(query, {"transaccion_id": transaccion_id, "cuenta_id": deposito.cuenta_id, "costo": transaccion_costo, "fecha": transaccion_fecha, "recibo": 1 if deposito.generar_recibo else None})
        query = text("UPDATE CUENTA SET CUENTA_SALDO = CUENTA_SALDO + :monto WHERE CUENTA_ID = :cuenta_id")
        db.execute(query, {"monto": deposito.monto, "cuenta_id": deposito.cuenta_id})
        recibo = None
        if deposito.generar_recibo and deposito.cajero_id:
            recibo_costo = 0.25
            query = text("INSERT INTO RECIBO (TRANSACCION_ID, CAJERO_ID, RECIBO_COSTO) VALUES (:transaccion_id, :cajero_id, :costo)")
            db.execute(query, {"transaccion_id": transaccion_id, "cajero_id": deposito.cajero_id, "costo": recibo_costo})
            recibo = ReciboResponse(transaccion_id=transaccion_id, cajero_id=deposito.cajero_id, recibo_costo=recibo_costo, transaccion_fecha=transaccion_fecha)
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
        if not cuenta or cuenta.CLIENTE_ID != cliente_id:
            raise HTTPException(status_code=403, detail="Acceso no autorizado a esta cuenta")
        if cuenta.CUENTA_SALDO < retiro.monto:
            raise HTTPException(status_code=400, detail="Saldo insuficiente")
        transaccion_id = str(uuid.uuid4())[:8].upper()
        transaccion_costo = 1.00 if retiro.usar_tarjeta else 0.75
        transaccion_fecha = datetime.now()
        query = text(
            "INSERT INTO TRANSACCION (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO) "
            "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo)"
        )
        db.execute(query, {"transaccion_id": transaccion_id, "cuenta_id": retiro.cuenta_id, "costo": transaccion_costo, "fecha": transaccion_fecha, "recibo": 1 if retiro.generar_recibo else None})
        if retiro.usar_tarjeta and retiro.tarjeta_id:
            query = text("SELECT * FROM TARJETA WHERE TARJETA_ID = :tarjeta_id AND CUENTA_ID = :cuenta_id AND TARJETA_ESTADO = :estado")
            result = db.execute(query, {"tarjeta_id": retiro.tarjeta_id, "cuenta_id": retiro.cuenta_id, "estado": "ACTIVA"})
            tarjeta = result.fetchone()
            if not tarjeta:
                raise HTTPException(status_code=404, detail="Tarjeta no encontrada o inactiva")
            query = text(
                "INSERT INTO RETIRO_CON_TARJETA (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO, RETIRO_MONTO, RETIRO_MONTO_MAX, RETIROCT_TARJETA, RETIROCT_AID, RETIROCT_P22, RETIROCT_P38, RETIROCT_COSTO_INTERBANCARIO) "
                "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo, :monto, :monto_max, :tarjeta, :aid, :p22, :p38, :costo_inter)"
            )
            db.execute(query, {
                "transaccion_id": transaccion_id, "cuenta_id": retiro.cuenta_id, "costo": transaccion_costo, "fecha": transaccion_fecha,
                "recibo": 1 if retiro.generar_recibo else None, "monto": retiro.monto, "monto_max": 1000,
                "tarjeta": retiro.tarjeta_id, "aid": "A0000000041010", "p22": "123", "p38": "123456", "costo_inter": 0.10
            })
        else:
            query = text(
                "INSERT INTO RETIRO_SIN_TARJETA (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO, RETIRO_MONTO) "
                "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo, :monto)"
            )
            db.execute(query, {
                "transaccion_id": transaccion_id, "cuenta_id": retiro.cuenta_id, "costo": transaccion_costo, "fecha": transaccion_fecha,
                "recibo": 1 if retiro.generar_recibo else None, "monto": retiro.monto
            })
        query = text("UPDATE CUENTA SET CUENTA_SALDO = CUENTA_SALDO - :monto WHERE CUENTA_ID = :cuenta_id")
        db.execute(query, {"monto": retiro.monto, "cuenta_id": retiro.cuenta_id})
        recibo = None
        if retiro.generar_recibo and retiro.cajero_id:
            recibo_costo = 0.25
            query = text("INSERT INTO RECIBO (TRANSACCION_ID, CAJERO_ID, RECIBO_COSTO) VALUES (:transaccion_id, :cajero_id, :costo)")
            db.execute(query, {"transaccion_id": transaccion_id, "cajero_id": retiro.cajero_id, "costo": recibo_costo})
            recibo = ReciboResponse(transaccion_id=transaccion_id, cajero_id=retiro.cajero_id, recibo_costo=recibo_costo, transaccion_fecha=transaccion_fecha)
        db.commit()
        return {"transaccion_id": transaccion_id, "recibo": recibo.dict() if recibo else None}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en retiro: {str(e)}")
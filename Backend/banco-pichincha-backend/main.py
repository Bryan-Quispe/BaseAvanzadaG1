# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime
from typing import Optional, List
import os
from dotenv import load_dotenv
import uuid
from config.database import get_db
from schemas.transaccion import ClienteCreate, ClienteUpdate, ClienteResponse, CuentaCreate, CuentaUpdate, CuentaResponse, CajeroCreate, CajeroUpdate, CajeroResponse, DepositoRequest, RetiroRequest, ReciboResponse

load_dotenv()

app = FastAPI(title="Banco Pichincha API")

# Configuración de JWT
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
        cliente = db.execute("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id", {"cliente_id": cliente_id}).fetchone()
        if not cliente:
            raise credentials_exception
        return cliente_id
    except JWTError:
        raise credentials_exception

# CRUD para Cliente
@app.post("/clientes/", response_model=ClienteResponse)
async def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    # Lógica para crear cliente (vacía por ahora)
    pass

@app.get("/clientes/", response_model=List[ClienteResponse])
async def leer_todos_clientes(db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    clientes = db.execute("SELECT * FROM CLIENTE").fetchall()
    if not clientes:
        raise HTTPException(status_code=404, detail="No se encontraron clientes")
    return [ClienteResponse(**cliente) for cliente in clientes]

@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
async def leer_cliente(cliente_id: str, db: Session = Depends(get_db)):
    cliente = db.execute("SELECT * FROM CLIENTE WHERE CLIENTE_ID = :cliente_id", {"cliente_id": cliente_id}).fetchone()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return ClienteResponse(**cliente)

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
    # Lógica para leer cuenta por ID (vacía por ahora)
    pass

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
    # Lógica para leer cajero por ID (vacía por ahora)
    pass

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
        cuenta = db.execute("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id AND CUENTA_ESTADO = :estado",
                           {"cuenta_id": deposito.cuenta_id, "estado": "ACTIVA"}).fetchone()
        if not cuenta or cuenta.CLIENTE_ID != cliente_id:
            raise HTTPException(status_code=403, detail="Acceso no autorizado a esta cuenta")
        transaccion_id = str(uuid.uuid4())[:8].upper()
        transaccion_costo = 0.50
        transaccion_fecha = datetime.now()
        db.execute(
            "INSERT INTO TRANSACCION (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO) "
            "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo)",
            {"transaccion_id": transaccion_id, "cuenta_id": deposito.cuenta_id, "costo": transaccion_costo, "fecha": transaccion_fecha, "recibo": 1 if deposito.generar_recibo else None}
        )
        db.execute(
            "INSERT INTO DEPOSITO (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO) "
            "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo)",
            {"transaccion_id": transaccion_id, "cuenta_id": deposito.cuenta_id, "costo": transaccion_costo, "fecha": transaccion_fecha, "recibo": 1 if deposito.generar_recibo else None}
        )
        db.execute("UPDATE CUENTA SET CUENTA_SALDO = CUENTA_SALDO + :monto WHERE CUENTA_ID = :cuenta_id",
                  {"monto": deposito.monto, "cuenta_id": deposito.cuenta_id})
        recibo = None
        if deposito.generar_recibo and deposito.cajero_id:
            recibo_costo = 0.25
            db.execute("INSERT INTO RECIBO (TRANSACCION_ID, CAJERO_ID, RECIBO_COSTO) VALUES (:transaccion_id, :cajero_id, :costo)",
                      {"transaccion_id": transaccion_id, "cajero_id": deposito.cajero_id, "costo": recibo_costo})
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
        cuenta = db.execute("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id AND CUENTA_ESTADO = :estado",
                           {"cuenta_id": retiro.cuenta_id, "estado": "ACTIVA"}).fetchone()
        if not cuenta or cuenta.CLIENTE_ID != cliente_id:
            raise HTTPException(status_code=403, detail="Acceso no autorizado a esta cuenta")
        if cuenta.CUENTA_SALDO < retiro.monto:
            raise HTTPException(status_code=400, detail="Saldo insuficiente")
        transaccion_id = str(uuid.uuid4())[:8].upper()
        transaccion_costo = 1.00 if retiro.usar_tarjeta else 0.75
        transaccion_fecha = datetime.now()
        db.execute(
            "INSERT INTO TRANSACCION (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO) "
            "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo)",
            {"transaccion_id": transaccion_id, "cuenta_id": retiro.cuenta_id, "costo": transaccion_costo, "fecha": transaccion_fecha, "recibo": 1 if retiro.generar_recibo else None}
        )
        if retiro.usar_tarjeta and retiro.tarjeta_id:
            tarjeta = db.execute("SELECT * FROM TARJETA WHERE TARJETA_ID = :tarjeta_id AND CUENTA_ID = :cuenta_id AND TARJETA_ESTADO = :estado",
                                {"tarjeta_id": retiro.tarjeta_id, "cuenta_id": retiro.cuenta_id, "estado": "ACTIVA"}).fetchone()
            if not tarjeta:
                raise HTTPException(status_code=404, detail="Tarjeta no encontrada o inactiva")
            db.execute(
                "INSERT INTO RETIRO_CON_TARJETA (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO, RETIRO_MONTO, RETIRO_MONTO_MAX, RETIROCT_TARJETA, RETIROCT_AID, RETIROCT_P22, RETIROCT_P38, RETIROCT_COSTO_INTERBANCARIO) "
                "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo, :monto, :monto_max, :tarjeta, :aid, :p22, :p38, :costo_inter)",
                {
                    "transaccion_id": transaccion_id, "cuenta_id": retiro.cuenta_id, "costo": transaccion_costo, "fecha": transaccion_fecha,
                    "recibo": 1 if retiro.generar_recibo else None, "monto": retiro.monto, "monto_max": 1000,
                    "tarjeta": retiro.tarjeta_id, "aid": "A0000000041010", "p22": "123", "p38": "123456", "costo_inter": 0.10
                }
            )
        else:
            db.execute(
                "INSERT INTO RETIRO_SIN_TARJETA (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO, RETIRO_MONTO) "
                "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo, :monto)",
                {
                    "transaccion_id": transaccion_id, "cuenta_id": retiro.cuenta_id, "costo": transaccion_costo, "fecha": transaccion_fecha,
                    "recibo": 1 if retiro.generar_recibo else None, "monto": retiro.monto
                }
            )
        db.execute("UPDATE CUENTA SET CUENTA_SALDO = CUENTA_SALDO - :monto WHERE CUENTA_ID = :cuenta_id",
                  {"monto": retiro.monto, "cuenta_id": retiro.cuenta_id})
        recibo = None
        if retiro.generar_recibo and retiro.cajero_id:
            recibo_costo = 0.25
            db.execute("INSERT INTO RECIBO (TRANSACCION_ID, CAJERO_ID, RECIBO_COSTO) VALUES (:transaccion_id, :cajero_id, :costo)",
                      {"transaccion_id": transaccion_id, "cajero_id": retiro.cajero_id, "costo": recibo_costo})
            recibo = ReciboResponse(transaccion_id=transaccion_id, cajero_id=retiro.cajero_id, recibo_costo=recibo_costo, transaccion_fecha=transaccion_fecha)
        db.commit()
        return {"transaccion_id": transaccion_id, "recibo": recibo.dict() if recibo else None}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en retiro: {str(e)}")
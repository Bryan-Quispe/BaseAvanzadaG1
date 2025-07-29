# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv
import uuid
from config.database import get_db

load_dotenv()

app = FastAPI(title="Banco Pichincha API")

# Configuración de JWT
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modelos Pydantic (definidos en schemas/transaccion.py, pero incluidos aquí para completitud)
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

# Autenticación
async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    except JWTError:
        raise credentials_exception
    return cliente_id

# API para depósito
@app.post("/transacciones/deposito", response_model=dict)
async def deposito(deposito: DepositoRequest, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        # Verificar cuenta
        cuenta = db.execute("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id AND CUENTA_ESTADO = :estado",
                           {"cuenta_id": deposito.cuenta_id, "estado": "ACTIVA"}).fetchone()
        if not cuenta:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada o inactiva")

        # Iniciar transacción
        transaccion_id = str(uuid.uuid4())[:8].upper()
        transaccion_costo = 0.50
        transaccion_fecha = datetime.now()

        # Insertar transacción
        db.execute(
            "INSERT INTO TRANSACCION (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO) "
            "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo)",
            {
                "transaccion_id": transaccion_id,
                "cuenta_id": deposito.cuenta_id,
                "costo": transaccion_costo,
                "fecha": transaccion_fecha,
                "recibo": 1 if deposito.generar_recibo else None
            }
        )

        # Insertar depósito
        db.execute(
            "INSERT INTO DEPOSITO (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO) "
            "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo)",
            {
                "transaccion_id": transaccion_id,
                "cuenta_id": deposito.cuenta_id,
                "costo": transaccion_costo,
                "fecha": transaccion_fecha,
                "recibo": 1 if deposito.generar_recibo else None
            }
        )

        # Actualizar saldo
        db.execute(
            "UPDATE CUENTA SET CUENTA_SALDO = CUENTA_SALDO + :monto WHERE CUENTA_ID = :cuenta_id",
            {"monto": deposito.monto, "cuenta_id": deposito.cuenta_id}
        )

        # Generar recibo si se solicita
        recibo = None
        if deposito.generar_recibo:
            if not deposito.cajero_id:
                raise HTTPException(status_code=400, detail="Se requiere cajero_id para generar recibo")
            recibo_costo = 0.25
            db.execute(
                "INSERT INTO RECIBO (TRANSACCION_ID, CAJERO_ID, RECIBO_COSTO) VALUES (:transaccion_id, :cajero_id, :costo)",
                {"transaccion_id": transaccion_id, "cajero_id": deposito.cajero_id, "costo": recibo_costo}
            )
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
        raise HTTPException(status_code=500, detail=f"Error al procesar el depósito: {str(e)}")

# API para retiro con tarjeta
@app.post("/transacciones/retiro/tarjeta", response_model=dict)
async def retiro_tarjeta(retiro: RetiroTarjetaRequest, db: Session = Depends(get_db), cliente_id: str = Depends(get_current_user)):
    try:
        # Verificar cuenta
        cuenta = db.execute("SELECT * FROM CUENTA WHERE CUENTA_ID = :cuenta_id AND CUENTA_ESTADO = :estado",
                           {"cuenta_id": retiro.cuenta_id, "estado": "ACTIVA"}).fetchone()
        if not cuenta:
            raise HTTPException(status_code=404, detail="Cuenta no encontrada o inactiva")

        # Verificar tarjeta
        tarjeta = db.execute(
            "SELECT * FROM TARJETA WHERE TARJETA_ID = :tarjeta_id AND CUENTA_ID = :cuenta_id AND TARJETA_ESTADO = :estado",
            {"tarjeta_id": retiro.tarjeta_id, "cuenta_id": retiro.cuenta_id, "estado": "ACTIVA"}
        ).fetchone()
        if not tarjeta:
            raise HTTPException(status_code=404, detail="Tarjeta no encontrada o inactiva")

        # Verificar saldo
        if cuenta.CUENTA_SALDO < retiro.monto:
            raise HTTPException(status_code=400, detail="Saldo insuficiente")

        # Iniciar transacción
        transaccion_id = str(uuid.uuid4())[:8].upper()
        transaccion_costo = 1.00
        transaccion_fecha = datetime.now()

        # Insertar transacción
        db.execute(
            "INSERT INTO TRANSACCION (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO) "
            "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo)",
            {
                "transaccion_id": transaccion_id,
                "cuenta_id": retiro.cuenta_id,
                "costo": transaccion_costo,
                "fecha": transaccion_fecha,
                "recibo": 1 if retiro.generar_recibo else None
            }
        )

        # Insertar retiro con tarjeta
        db.execute(
            "INSERT INTO RETIRO_CON_TARJETA (TRANSACCION_ID, CUENTA_ID, TRANSACCION_COSTO, TRANSACCION_FECHA, TRANSACCION_RECIBO, "
            "RETIRO_MONTO, RETIRO_MONTO_MAX, RETIROCT_TARJETA, RETIROCT_AID, RETIROCT_P22, RETIROCT_P38, RETIROCT_COSTO_INTERBANCARIO) "
            "VALUES (:transaccion_id, :cuenta_id, :costo, :fecha, :recibo, :monto, :monto_max, :tarjeta, :aid, :p22, :p38, :costo_inter)",
            {
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
            }
        )

        # Actualizar saldo
        db.execute(
            "UPDATE CUENTA SET CUENTA_SALDO = CUENTA_SALDO - :monto WHERE CUENTA_ID = :cuenta_id",
            {"monto": retiro.monto, "cuenta_id": retiro.cuenta_id}
        )

        # Generar recibo si se solicita
        recibo = None
        if retiro.generar_recibo:
            recibo_costo = 0.25
            db.execute(
                "INSERT INTO RECIBO (TRANSACCION_ID, CAJERO_ID, RECIBO_COSTO) VALUES (:transaccion_id, :cajero_id, :costo)",
                {"transaccion_id": transaccion_id, "cajero_id": retiro.cajero_id, "costo": recibo_costo}
            )
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
        raise HTTPException(status_code=500, detail=f"Error al procesar el retiro: {str(e)}")
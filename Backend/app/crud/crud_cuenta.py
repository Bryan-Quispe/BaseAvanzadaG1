from sqlalchemy.orm import Session
from datetime import date
from app.models import cuenta_model
from app.schemas import cuenta_schema

def obtener_cuenta_por_id(bd: Session, id_cuenta: str):
    return bd.query(cuenta_model.Cuenta).filter(cuenta_model.Cuenta.id == id_cuenta).first()

def obtener_cuentas_por_cliente(bd: Session, id_cliente: str):
    return bd.query(cuenta_model.Cuenta).filter(cuenta_model.Cuenta.id_cliente == id_cliente).all()

def crear_cuenta_para_cliente(bd: Session, cuenta: cuenta_schema.CuentaCrear, id_cliente: str):
    db_cuenta = cuenta_model.Cuenta(
        **cuenta.model_dump(), 
        id_cliente=id_cliente,
        fecha_apertura=date.today()
    )
    bd.add(db_cuenta)
    bd.commit()
    bd.refresh(db_cuenta)
    return db_cuenta
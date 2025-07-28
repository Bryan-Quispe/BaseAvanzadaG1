from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud import crud_cuenta
from app.schemas import cuenta_schema
from app.db.session import obtener_bd

ruta = APIRouter()

@ruta.get("/{id_cuenta}", response_model=cuenta_schema.CuentaLectura, summary="Obtener una cuenta por su ID")
def obtener(id_cuenta: str, bd: Session = Depends(obtener_bd)):
    """Busca y devuelve los datos de una única cuenta por su ID."""
    db_cuenta = crud_cuenta.obtener_cuenta_por_id(bd, id_cuenta=id_cuenta)
    if db_cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return db_cuenta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.crud import crud_cliente, crud_cuenta
from app.schemas import cliente_schema, cuenta_schema
from app.db.session import obtener_bd

ruta = APIRouter()

# --- RUTAS PARA CLIENTES ---
#                                      AQUÍ ESTÁ EL CAMBIO ▼
@ruta.post("/", response_model=cliente_schema.ClienteLectura, summary="Crear un nuevo cliente")
def crear_cliente(cliente: cliente_schema.ClienteCrear, bd: Session = Depends(obtener_bd)):
    cliente_existente = crud_cliente.obtener_cliente_por_id(bd, id_cliente=cliente.id)
    if cliente_existente:
        raise HTTPException(status_code=409, detail="Ya existe un cliente con este ID")
    return crud_cliente.crear_cliente(bd=bd, cliente=cliente)

#                                      Y AQUÍ ▼
@ruta.get("/", response_model=List[cliente_schema.ClienteLectura], summary="Obtener lista de clientes")
def listar_clientes(omitir: int = 0, limite: int = 100, bd: Session = Depends(obtener_bd)):
    clientes = crud_cliente.obtener_clientes(bd, omitir=omitir, limite=limite)
    return clientes

#                                      Y TAMBIÉN AQUÍ ▼
@ruta.get("/{id_cliente}", response_model=cliente_schema.ClienteLectura, summary="Obtener un cliente por ID")
def obtener_cliente(id_cliente: str, bd: Session = Depends(obtener_bd)):
    db_cliente = crud_cliente.obtener_cliente_por_id(bd, id_cliente=id_cliente)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

# --- RUTAS PARA CUENTAS DE UN CLIENTE ---
# (Estas rutas ya estaban correctas, no necesitan cambios)
@ruta.post("/{id_cliente}/cuentas/", response_model=cuenta_schema.CuentaLectura, summary="Crear cuenta para un cliente")
def crear_cuenta_cliente(id_cliente: str, cuenta: cuenta_schema.CuentaCrear, bd: Session = Depends(obtener_bd)):
    cliente_db = crud_cliente.obtener_cliente_por_id(bd, id_cliente=id_cliente)
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado para crearle una cuenta.")
    return crud_cuenta.crear_cuenta_para_cliente(bd=bd, cuenta=cuenta, id_cliente=id_cliente)

@ruta.get("/{id_cliente}/cuentas/", response_model=List[cuenta_schema.CuentaLectura], summary="Listar cuentas de un cliente")
def listar_cuentas_cliente(id_cliente: str, bd: Session = Depends(obtener_bd)):
    cliente_db = crud_cliente.obtener_cliente_por_id(bd, id_cliente=id_cliente)
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    return crud_cuenta.obtener_cuentas_por_cliente(bd=bd, id_cliente=id_cliente)
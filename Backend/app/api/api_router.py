from fastapi import APIRouter
from app.api.endpoints import clientes, cuentas

router_api = APIRouter()

router_api.include_router(clientes.ruta, prefix="/clientes", tags=["Clientes y Cuentas"])
router_api.include_router(cuentas.ruta, prefix="/cuentas", tags=["Cuentas (Consultas directas)"])
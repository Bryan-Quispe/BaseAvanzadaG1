from fastapi import FastAPI
from app.core.config import configuracion
from app.api.api_router import router_api

# Usamos 'aplicacion' para que coincida con tu comando uvicorn
aplicacion = FastAPI(
    title=configuracion.NOMBRE_PROYECTO
)

aplicacion.include_router(router_api, prefix="/api/v1")

@aplicacion.get("/", tags=["Root"])
def leer_raiz():
    return {"mensaje": f"Bienvenido a la {configuracion.NOMBRE_PROYECTO}"}
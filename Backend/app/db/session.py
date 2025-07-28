from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import configuracion

motor = create_engine(configuracion.DATABASE_URL)
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)

def obtener_bd():
    """
    Función de dependencia centralizada para obtener una sesión de base de datos.
    Asegura que la sesión se cierre siempre después de usarse.
    """
    bd = SesionLocal()
    try:
        yield bd
    finally:
        bd.close()
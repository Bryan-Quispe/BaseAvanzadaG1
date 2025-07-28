from pydantic_settings import BaseSettings

class Configuracion(BaseSettings):
    """
    Define las configuraciones de la aplicación.
    Lee las variables de entorno desde un archivo .env.
    """
    # Cambia el nombre aquí para que coincida con el .env
    DATABASE_URL: str 
    
    NOMBRE_PROYECTO: str = "API del Banco Pichincha"

    class Config:
        env_file = ".env"

configuracion = Configuracion()
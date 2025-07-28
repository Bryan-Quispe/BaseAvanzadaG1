from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List
from .cuenta_schema import CuentaLectura

class ClienteBase(BaseModel):
    """
    Esquema base para un cliente.
    Contiene todos los campos comunes que se comparten entre la creación y la lectura.
    """
    nombres: str
    apellidos: str
    correo: EmailStr  # Usa EmailStr para una validación automática del formato de correo.
    celular: str
    direccion: str
    provincia: str
    ciudad: str
    fecha_nacimiento: date

class ClienteCrear(ClienteBase):
    """
    Esquema para recibir los datos al momento de crear un nuevo cliente.
    Hereda de ClienteBase y añade el campo 'id'.
    """
    id: str

class ClienteLectura(ClienteBase):
    """
    Esquema para formatear la respuesta al solicitar los datos de un cliente.
    Incluye los campos del cliente y una lista de sus cuentas asociadas.
    """
    id: str
    cuentas: List[CuentaLectura] = [] # Relación para mostrar las cuentas del cliente.

    class Config:
        """
        Configuración de Pydantic.
        'from_attributes = True' permite que el modelo se cree a partir de un
        objeto de SQLAlchemy (es el reemplazo moderno de 'orm_mode').
        """
        from_attributes = True
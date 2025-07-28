from sqlalchemy import Column, String, Date
from sqlalchemy.orm import relationship
from app.db.base import Base

class Cliente(Base):
    """Modelo SQLAlchemy para la entidad Cliente."""
    __tablename__ = 'CLIENTE'

    id = Column('CLIENTE_ID', String(10), primary_key=True, index=True)
    nombres = Column('CLIENTE_NOMBRES', String(128), nullable=False)
    apellidos = Column('CLIENTE_APELLIDOS', String(128), nullable=False)
    correo = Column('CLIENTE_CORREO', String(128), nullable=False, unique=True)
    celular = Column('CLIENTE_CEULAR', String(10), nullable=False)
    direccion = Column('CLIENTE_DIRECCION', String(128), nullable=False)
    provincia = Column('CLIENTE_PROVINCIA', String(128), nullable=False)
    ciudad = Column('CLIENTE_CIUDAD', String(64), nullable=False)
    fecha_nacimiento = Column('CLIENTE_FCHNACIMIENTO', Date, nullable=False)

    cuentas = relationship("Cuenta", back_populates="propietario")
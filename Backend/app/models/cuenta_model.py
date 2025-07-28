from sqlalchemy import Column, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Cuenta(Base):
    """Modelo SQLAlchemy para la entidad Cuenta."""
    __tablename__ = 'CUENTA'

    id = Column('CUENTA_ID', String(10), primary_key=True, index=True)
    id_cliente = Column('CLIENTE_ID', String(10), ForeignKey('CLIENTE.CLIENTE_ID'), nullable=False)
    nombre = Column('CUENTA_NOMBRE', String(64), nullable=False)
    saldo = Column('CUENTA_SALDO', Numeric(12, 2), nullable=False)
    fecha_apertura = Column('CUENTA_APERTURA', Date, nullable=False)
    estado = Column('CUENTA_ESTADO', String(32), nullable=False)
    limite_web = Column('CUENTA_LIMITE_TRANS_WEB', Numeric(7, 2), nullable=False)
    limite_movil = Column('CUENTA_LIMITE_TRANS_MOVIL', Numeric(7, 2), nullable=False)

    propietario = relationship("Cliente", back_populates="cuentas")
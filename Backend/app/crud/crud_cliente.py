from sqlalchemy.orm import Session
from app.models import cliente_model
from app.schemas import cliente_schema

def obtener_cliente_por_id(bd: Session, id_cliente: str):
    return bd.query(cliente_model.Cliente).filter(cliente_model.Cliente.id == id_cliente).first()

def obtener_clientes(bd: Session, omitir: int = 0, limite: int = 100):
    return bd.query(cliente_model.Cliente).offset(omitir).limit(limite).all()

def crear_cliente(bd: Session, cliente: cliente_schema.ClienteCrear):
    db_cliente = cliente_model.Cliente(**cliente.model_dump())
    bd.add(db_cliente)
    bd.commit()
    bd.refresh(db_cliente)
    return db_cliente
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime
from app.core.database import Base

class planesModel(Base):
    __tablename__ = "planes"

    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    tipo=Column(String(100),nullable=False)
    precio=Column(DECIMAL(10,2),nullable=False)
    duracion=Colum(Integer,nullable=False)
    estado=Colum(String(500),defaul='activo')

class membresiasModel(Base):
    __tablename__="membresias_usuario"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("planes.id", ondelete="CASCADE"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    estado = Column(String(50), default="activa") 
    creado_en = Column(DateTime, default=datetime.utcnow)

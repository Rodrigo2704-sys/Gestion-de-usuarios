from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base # Tu instancia base de SQLAlchemy

class RolModel(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)

    # Relación uno-a-muchos con usuarios
    usuarios = relationship("UsuarioModel", back_populates="rol")


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    rol_id = Column(Integer,ForeignKey("roles.id"),default=2,nullable=False
)

    # Relación para traer el objeto Rol (y su nombre "Administrador", "Cliente", etc.)
    rol = relationship("RolModel", back_populates="usuarios")
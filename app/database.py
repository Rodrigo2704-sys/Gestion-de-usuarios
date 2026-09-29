from sqlalchemy.orm import Session
from app.models.usuarios import UsuarioModel
from app.core.security import hash_password

def crear_usuario(db:Session,usuarios)
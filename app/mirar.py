from sqlalchemy.orm import Session
from app.models.usuario import UsuarioModel
from app.schemas.usuario import UsuarioCreate
from app.core.security import hash_password

def obtener_usuario_por_correo(db: Session, correo: str):
    
    return db.query(UsuarioModel).filter(UsuarioModel.correo == correo).first()

def crear_usuario(db: Session, usuario: UsuarioCreate):
    password_hash = hash_password(usuario.password)
    
    db_usuario = UsuarioModel(
        nombre=usuario.nombre,
        correo=usuario.correo,
        password=password_hash 
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# --- NUEVAS FUNCIONES PARA COMPLETAR EL CRUD ---

def actualizar_usuario(db: Session, usuario_id: int, datos_actualizacion: dict):
    """Busca al usuario por ID, actualiza los campos enviados y los guarda."""
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    
    if not db_usuario:
        return None # Si no existe, retornamos None para controlarlo en la ruta
    
    # Si viene una nueva contraseña, la hasheamos antes de actualizarla
    if "password" in datos_actualizacion and datos_actualizacion["password"]:
        datos_actualizacion["password"] = hash_password(datos_actualizacion["password"])

    # Actualizamos dinámicamente los campos que vengan en el diccionario
    for key, value in datos_actualizacion.items():
        setattr(db_usuario, key, value)
        
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def eliminar_usuario(db: Session, usuario_id: int):
    """Busca al usuario por ID y lo elimina de la base de datos."""
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    
    if not db_usuario:
        return None
        
    db.delete(db_usuario)
    db.commit()
    return db_usuario
from sqlalchemy.orm import Session
from app.models.usuarios import UsuarioModel
from app.schemas.usuarios import EntradaRegistro
from app.core.security import hash_password
from app.core.security import verificar_contraseña

def iniciar_sesion(db: Session, email: str, contraseña_ingresada: str):
    # 1. Primera condición: Buscar al usuario por el correo
    usuario = db.query(UsuarioModel).filter(UsuarioModel.correo == email).first()
    
    # Si el correo no existe en la base de datos, retornamos False (o None)
    if not usuario:
        return None

    # 2. Segunda condición: Verificar la contraseña con la función segura
    # 'usuario.password' es el hash largo que está guardado en MySQL
    contrasena_valida = verify_password(contrasena_ingresada, usuario.password)
    
    if not contrasena_valida:
        return None # La contraseña es incorrecta

    # Si pasa ambas validaciones, el login es exitoso y devolvemos el usuario
    return usuario



def registrar_usuario(db: Session, usuario: EntradaRegistro):
    contrasena_encriptada = hash_password(usuario.password)

    db_usuario = UsuarioModel(
        nombre=usuario.nombre,
        correo=usuario.correo,
        password=contrasena_encriptada
    )

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario 


def obtener_usuario_por_correo(db: Session, correo: str):
    return db.query(UsuarioModel).filter(UsuarioModel.correo == correo).first()



def obtener_usuario_por_id(db: Session, usuario_id: int):
    return db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()


def obtener_todos_los_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UsuarioModel).offset(skip).limit(limit).all()


def actualizar_usuario(db: Session, usuario_id: int, datos_actualizacion: dict):
    # 1. Buscamos al usuario usando la función reutilizable
    db_usuario = obtener_usuario_por_id(db, usuario_id)
    if not db_usuario:
        return None 
    
    # 2. Seguridad: Eliminamos la llave "id" si viene en el diccionario para evitar que la cambien
    datos_actualizacion.pop("id", None)
    
    # 3. Si viene una nueva contraseña, la hasheamos
    if "password" in datos_actualizacion and datos_actualizacion["password"]:
        datos_actualizacion["password"] = hash_password(datos_actualizacion["password"])

    # 4. Actualizamos dinámicamente los campos permitidos
    for key, value in datos_actualizacion.items():
        setattr(db_usuario, key, value)
        
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def eliminar_usuario(db: Session, usuario_id: int):
    # 1. Reutilizamos la búsqueda por ID
    db_usuario = obtener_usuario_por_id(db, usuario_id)
    if not db_usuario:
        return None
        
    db.delete(db_usuario)
    db.commit()
    return db_usuario
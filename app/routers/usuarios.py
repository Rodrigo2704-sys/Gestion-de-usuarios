from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError 
from fastapi.security import OAuth2PasswordRequestForm
from app.main import limiter  # O la referencia donde inicializaste el limiter
from fastapi import Request  # Import para capturar errores de BD

# Importamos la dependencia para la base de datos y la seguridad
from app.core.database import get_db 
from app.core.security import verificar_contraseña, crear_token_acceso, verificar_token # <--- Agregamos verificar_token

# Importamos tus esquemas de Pydantic
from app.schemas.usuarios import EntradaLogin, DatosUsuario, EntradaRegistro, SalidaUsuario, ActualizarUsuario
from app.models.usuarios import UsuarioModel

# Importamos las funciones del CRUD
from app.crud.usuarios import (
    iniciar_sesion,
    registrar_usuario,
    obtener_usuario_por_correo,
    obtener_usuario_por_id,
    obtener_todos_los_usuarios,
    actualizar_usuario,
    eliminar_usuario,
    actualizar_rol_usuario_crud
)


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])



def obtener_usuario_actual(email: str = Depends(verificar_token), db: Session = Depends(get_db)):
    # Buscas al usuario en la base de datos usando el correo que viene del token
    usuario = db.query(UsuarioModel).filter(UsuarioModel.correo == email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo"
        )
    return usuario


def solo_administradores(
    usuario_actual = Depends(obtener_usuario_actual)
):
    """
    Guard de seguridad estricto para rutas de administración (RBAC).
    """
    if usuario_actual.rol_id != 1:  # 1 = Administrador
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren privilegios de Administrador."
        )
    return usuario_actual


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    
    usuario = iniciar_sesion(db, email=form_data.username, contraseña_ingresada=form_data.password)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Correo o contraseña incorrectos"
        )
    
    nombre_rol = usuario.rol.nombre
    
    access_token = crear_token_acceso(datos={
        "sub": usuario.correo,
        "rol": nombre_rol
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "nombre": usuario.nombre,
        "rol": nombre_rol
    }


# 2. REGISTRAR USUARIO (Pública)

@router.post("/registrar", response_model=SalidaUsuario, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def crear_nuevo_usuario(datos: EntradaRegistro, db = Depends(get_db)):
    usuario_existente = obtener_usuario_por_correo(db, correo=datos.correo)
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El correo ya se encuentra registrado"
        )

    try:
        nuevo_usuario = registrar_usuario(db, usuario=datos)
        
        if not nuevo_usuario:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="No se pudo registrar el usuario"
            )

        return nuevo_usuario

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado en la base de datos al registrar el usuario"
        )


# --- ENDPOINT PARA CAMBIAR ROL (Protegido con RBAC Estricto) ---
@router.patch("/{usuario_id}/cambiar-rol", response_model=SalidaUsuario)
def cambiar_rol_endpoint(
    usuario_id: int, 
    nuevo_rol_id: int, 
    db = Depends(get_db),
    admin_actual = Depends(solo_administradores)
):
    if admin_actual.id == usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operación no permitida. No puedes cambiar tu propio rol de administrador."
        )

    if nuevo_rol_id not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido. Solo se permite 1 (Admin) o 2 (Cliente)."
        )

    usuario_actualizado = actualizar_rol_usuario_crud(db, usuario_id, nuevo_rol_id)
    
    if not usuario_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
        
    return usuario_actualizado


@router.get("/buscar/correo", response_model=SalidaUsuario)
def obtener_usuario_por_correo_endpoint(
    email: str, 
    db = Depends(get_db),
    admin_actual = Depends(solo_administradores)  # 🔒 Cambiado a solo_administradores
):
    usuario = obtener_usuario_por_correo(db, correo=email)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ningún usuario con ese correo electrónico"
        )
    return usuario

@router.get("/", response_model=List[SalidaUsuario])
def listar_usuarios(
    skip: int = 0, 
    limit: int = 100, 
    db = Depends(get_db),
    admin_actual = Depends(solo_administradores)  # 🔒 Cambiado a solo_administradores
):
    usuarios = obtener_todos_los_usuarios(db, skip=skip, limit=limit)
    return usuarios


# 4. OBTENER USUARIO POR ID (Protegida)
@router.get("/{usuario_id}", response_model=SalidaUsuario)
def obtener_usuario_por_id_endpoint(
    usuario_id: int, 
    db = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    usuario = obtener_usuario_por_id(db, usuario_id=usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario


@router.patch("/{usuario_id}", response_model=SalidaUsuario)
def modificar_usuario(
    usuario_id: int, 
    datos: ActualizarUsuario, 
    db = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    # 🔒 Validación de propiedad o rol de administrador
    if usuario_actual.rol_id != 1 and usuario_actual.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar los datos de otro usuario."
        )

        #Esta linea es para agarrar solo  los datos que el  cliente decidio actualizar.

    datos_dict = datos.model_dump(exclude_unset=True) if hasattr(datos, "model_dump") else datos.dict(exclude_unset=True)
    
    if not datos_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron datos para actualizar."
        )
    
    usuario_actualizado = actualizar_usuario(db=db, usuario_id=usuario_id, datos_actualizacion=datos_dict)
    if not usuario_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
        
    return usuario_actualizado

# 6. ELIMINAR USUARIO (Protegida)
@router.delete("/{usuario_id}")
def borrar_usuario(
    usuario_id: int, 
    db = Depends(get_db),
    admin_actual = Depends(solo_administradores)
):
    try:
        usuario_eliminado = eliminar_usuario(db, usuario_id=usuario_id)
        
        if not usuario_eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado."
            )
            
        return {
            "Exito": True, 
            "Mensaje": "Usuario eliminado correctamente"
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en la base de datos al intentar eliminar el usuario."
        )
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError  # Import para capturar errores de BD

# Importamos la dependencia para la base de datos y la seguridad
from app.core.database import get_db 
from app.core.security import verificar_contraseña, crear_token_acceso, verificar_token # <--- Agregamos verificar_token

# Importamos tus esquemas de Pydantic
from app.schemas.usuarios import EntradaLogin, DatosUsuario, EntradaRegistro, SalidaUsuario, ActualizarUsuario

# Importamos las funciones del CRUD
from app.crud.usuarios import (
    iniciar_sesion,
    registrar_usuario,
    obtener_usuario_por_correo,
    obtener_usuario_por_id,
    obtener_todos_los_usuarios,
    actualizar_usuario,
    eliminar_usuario
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# 1. INICIAR SESIÓN (Pública)
@router.post("/login")  
def login(datos: EntradaLogin, db: Session = Depends(get_db)):
    usuario = iniciar_sesion(db, email=datos.correo, contraseña_ingresada=datos.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Correo o contraseña incorrectos"
        )
    
    access_token = crear_token_acceso(datos={
        "sub": usuario.correo,
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "nombre": usuario.nombre
    }


# 2. REGISTRAR USUARIO (Pública)
@router.post("/registrar", response_model=SalidaUsuario, status_code=status.HTTP_201_CREATED) # <--- Corregido: le faltaba la barra '/' en "/registrar"
def crear_nuevo_usuario(datos: EntradaRegistro, db: Session = Depends(get_db)):
    # 1. Verificamos regla de negocio (si el correo ya existe)
    usuario_existente = obtener_usuario_por_correo(db, correo=datos.correo)
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El correo ya se encuentra registrado"
        )

    # 2. Control de fallos de servidor/BD con try-except
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


# 3. OBTENER TODOS LOS USUARIOS (Protegida con Token)
@router.get("/", response_model=List[SalidaUsuario])
def listar_usuarios(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    email_usuario: str = Depends(verificar_token) # <--- Token de seguridad
):
    usuarios = obtener_todos_los_usuarios(db, skip=skip, limit=limit)
    return usuarios


# 4. OBTENER USUARIO POR ID (Protegida con Token)
@router.get("/{usuario_id}", response_model=SalidaUsuario)
def obtener_usuario_por_id_endpoint(
    usuario_id: int, 
    db: Session = Depends(get_db),
    email_usuario: str = Depends(verificar_token) # <--- Token de seguridad
):
    usuario = obtener_usuario_por_id(db, usuario_id=usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario


# 5. ACTUALIZAR USUARIO (Protegida con Token)
@router.put("/{usuario_id}", response_model=SalidaUsuario)
def modificar_usuario(
    usuario_id: int, 
    datos: ActualizarUsuario, 
    db: Session = Depends(get_db),
    email_usuario: str = Depends(verificar_token) # <--- Token de seguridad
):
    # Pydantic v2: model_dump(exclude_unset=True) / Pydantic v1: dict(exclude_unset=True)
    datos_dict = datos.model_dump(exclude_unset=True) if hasattr(datos, "model_dump") else datos.dict(exclude_unset=True)
    
    if not datos_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron datos para actualizar."
        )
    
    try:
        usuario_actualizado = actualizar_usuario(db=db, usuario_id=usuario_id, datos_actualizacion=datos_dict)
        
        if not usuario_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado."
            )
            
        return usuario_actualizado

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar los datos en la base de datos."
        )


# 6. ELIMINAR USUARIO (Protegida con Token)
@router.delete("/{usuario_id}")
def borrar_usuario(
    usuario_id: int, 
    db: Session = Depends(get_db),
    email_usuario: str = Depends(verificar_token) # <--- Token de seguridad
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
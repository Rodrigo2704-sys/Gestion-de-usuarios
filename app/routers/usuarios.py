from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Importamos la dependencia para la base de datos
from app.core.database import get_db 
from app.core.security import verificar_contraseña , crear_token_acceso

# Importamos tus esquemas de Pydantic
from app.schemas.usuarios import DatosUsuario , EntradaRegistro , SalidaUsuario
# (Nota: Si tienes un esquema específico para login o update parcial, 
# asegúrate de importarlo aquí. Usaremos EntradaRegistro o adaptaremos según tus clases).

# ¡Importamos exactamente los nombres reales de tus funciones del CRUD!
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


@router.post("/")  
def login(datos: EntradaLogin, db: Session = Depends(get_db)):
    usuario = iniciar_sesion(db, email=datos.correo, contraseña_ingresada=datos.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    
    access_token = crear_token_acceso(data={
        "sub": usuario.correo,
        "rol": usuario.rol
    })
    
    return {
        "access_token": crear_token_acceso,
        "token_type": "bearer",
        "rol": usuario.rol,
        "nombre": usuario.nombre
    }

# 2. REGISTRAR USUARIO
@router.post("/", response_model=SalidaUsuario, status_code=status.HTTP_201_CREATED)
def crear_nuevo_usuario(datos: EntradaRegistro, db: Session = Depends(get_db)):
    # Verificamos si el correo ya existe
    usuario_existente = obtener_usuario_por_correo(db, correo=datos.correo)
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El correo ya se encuentra registrado"
        )

    # Llamamos a tu función CRUD real
    nuevo_usuario = registrar_usuario(db, usuario=datos)
    
    if not nuevo_usuario:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="No se pudo registrar el usuario"
        )

    return nuevo_usuario


# 3. OBTENER TODOS LOS USUARIOS (¡Faltaba esta!)
@router.get("/", response_model=List[SalidaUsuario])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = obtener_todos_los_usuarios(db, skip=skip, limit=limit)
    return usuarios


# 4. OBTENER USUARIO POR ID (¡Faltaba esta!)
@router.get("/{usuario_id}", response_model=SalidaUsuario)
def obtener_usuario_por_id_endpoint(usuario_id: int, db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_id(db, usuario_id=usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario


# 5. ACTUALIZAR USUARIO (Usando tu lógica dinámica con diccionarios)
@router.put("/{usuario_id}", response_model=SalidaUsuario)
def modificar_usuario(usuario_id: int, datos: ActualizarUsuario, db: Session = Depends(get_db)):
    # Convertimos los datos a diccionario (puedes usar exclude_unset=True si creas un esquema parcial)
    datos_dict = datos.dict(exclude_unset=True)
    
    if not datos_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron datos para actualizar."
        )
    
    # Llamamos a tu función CRUD de actualización
    usuario_actualizado = actualizar_usuario(db=db, usuario_id=usuario_id, datos_actualizacion=datos_dict)
    
    if not usuario_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
        
    return usuario_actualizado


# 6. ELIMINAR USUARIO
@router.delete("/{usuario_id}")
def borrar_usuario(usuario_id: int, db: Session = Depends(get_db)):
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
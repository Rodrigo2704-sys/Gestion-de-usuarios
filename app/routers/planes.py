from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database  import get_db
from app.core.security import verificar_token
from app.schemas.planes import DatosPlan, SalidaPlan, AsignarMembresia, SalidaMembresia, ActualizarMembresia
from app.routers import obtener_usuario_actual, solo_administradores

from app.planes.planes import(
    crear_plan,
    consultar_planes,
    asignar_membresia,
    actualizar_membresia,
    membresia_usuario

#get
#post
#delete
#put

)

router =APIRouter(prefix="/planes",tags=["planes"])

@router.post("/crear", response_model=SalidaPlan, status_code=status.HTTP_201_CREATED)
def creacion_plan(
    datos: DatosPlan, 
    db: Session = Depends(get_db),
    admin = Depends(solo_administradores)
):
    try:
        nuevo_plan = crear_plan(db, datos)
        return nuevo_plan
        
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error en la base de datos al intentar crear el plan."
        )


# --- 2. LISTAR PLANES (Abierto para cualquier usuario logueado) ---
@router.get("/obtener", response_model=list[SalidaPlan])
def listar_planes_activos(
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    planes = consultar_planes(db)
    return planes


# --- 3. ASIGNAR MEMBRESÍA (Solo Administradores) ---
@router.post("/asignar", response_model=SalidaMembresia, status_code=status.HTTP_201_CREATED)
def endpoint_asignar_membresia(
    datos: AsignarMembresia, 
    db: Session = Depends(get_db),
    admin = Depends(solo_administradores)
):
    try:
        nueva_membresia = asignar_membresia(db, datos)
        
        if not nueva_membresia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="No se pudo asignar la membresía. Verifica que el ID del usuario y del plan existan."
            )
            
        return nueva_membresia

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en la base de datos al intentar asignar la membresía."
        )

@router.put("/actualizar-plan/{usuario_id}", response_model=SalidaMembresia)
def endpoint_actualizar_membresia(
    usuario_id: int,
    datos: ActualizarMembresia,  
    db: Session = Depends(get_db),
    admin = Depends(solo_administradores)
):
    #  Corregido: datos_dict sin la 'c'
    datos_dict = datos.model_dump(exclude_unset=True) if hasattr(datos, "model_dump") else datos.dict(exclude_unset=True)

    # Validamos que al menos hayan enviado un campo en el JSON
    if not datos_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar (plan_id o estado)."
        )

    # Le pasamos a la función CRUD el objeto Pydantic
    membresia_actualizada = actualizar_membresia(db, usuario_id=usuario_id, datos=datos)

    if not membresia_actualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró una membresía registrada para este usuario."
        )

    return membresia_actualizada


# --- 4. VER MI PROPIA MEMBRESÍA (Para cualquier cliente logueado) ---
@router.get("/mi-membresia", response_model=list[SalidaMembresia])
def ver_mi_membresia(
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    # Aquí en tu CRUD deberías filtrar pasándole 'usuario_actual.id' 
    # para que el cliente solo vea sus propias membresías y no las de los demás.
    membresias = membresia_usuario_por_id(db, usuario_id=usuario_actual.id)
    return membresias
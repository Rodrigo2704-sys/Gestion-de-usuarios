from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database  import get_db
from app.core.security import verificar_token
from app.schemas.planes import DatosPlan, SalidaPlan, AsignarMembresia, SalidaMembresia

from app.planes.planes import(
    crear_plan,
    consultar_planes,
    asignar_membresia,
    membresia_usuario

#get
#post
#delete
#put

)

router =APIRouter(prefix="/planes",tags=["planes"])

@router.post("/crear", response_model=SalidaPlan, status_code=status.HTTP_201_CREATED)
def creacion_plan(datos: DatosPlan, db: Session = Depends(get_db),email_usuario: str = Depends(verificar_token) # <--- ¡AQUÍ SE PONE EL TOKEN!
):
    # 'verificar_token' ya se ejecutó automáticamente.
    # Si el token era inválido o expiró, FastAPI YA lanzó el error 401 Unauthorized
    # y NUNCA llegará a ejecutar estas líneas de abajo.

    try:
        # 1. Llamamos a la función del CRUD para guardar en MySQL
        nuevo_plan = crear_plan(db, datos)
        return nuevo_plan
        
    except SQLAlchemyError as e:
        # 2. Si MySQL u ORM fallan, atrapamos el error y lanzamos un HTTP 500 o 400 limpio
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocurrió un error al intentar crear el plan en la base de datos."
        )



@router.get("/obtener",response_model=list[SalidaPlan])
def listar_planes_activos(db:Session =Depends(get_db),email_usuario:str = Depends(verificar_token)):

    planes=consultar_planes(db)
    return planes


@router.post("/asignar", response_model=SalidaMembresia, status_code=status.HTTP_201_CREATED)
def endpoint_asignar_membresia(datos: AsignarMembresia, db: Session = Depends(get_db),email_usuario: str = Depends(verificar_token) # Protegido con el token
):
    try:
        # 1. Llamamos a la función del CRUD que calcula la fecha fin y guarda en MySQL
        nueva_membresia = asignar_membresia(db, datos)
        
        #verificamos que la membresia exista ya que la logica en el crud de planes consultamos que el id del usuario y el plan.
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

@router.get("/membresia_usuarios",response_model=list[SalidaMembresia])
def membresia_del_usuario(db: Session = Depends(get_db),email_usuario:str = Depends(verificar_token)):

    extraer_usuarios=membresia_usuario(db)
    return extraer_usuarios

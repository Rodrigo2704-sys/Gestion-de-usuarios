from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Importación de Modelos de SQLAlchemy
from app.models.planes import planesModel, membresiasModel, DatosPlan
from app.models.usuario import UsuarioModel  # Ajusta la ruta a tu modelo de Usuario

# Importación de Schemas de Pydantic
from app.schemas.membresia import EntradaPlan, AsignarMembresia


def crear_plan(db: Session, plan: DatosPlan):
    # Usamos el schema 'plan' para extraer los datos
    db_plan = planesModel(
        tipo=plan.tipo,
        precio=plan.precio,
        duracion=plan.duracion
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def consultar_planes(db: Session):
    return db.query(planesModel).filter(planesModel.estado == 'activo').all()


# ==========================================
# 2. FUNCIONES DE MEMBRESÍAS
# ==========================================

def asignar_membresia(db: Session, datos: AsignarMembresia):
    # 1. Buscamos el plan específico seleccionado por el ID (datos.plan_id)
    plan = db.query(planesModel).filter(planesModel.id == datos.plan_id, planesModel.estado == 'activo').first()

    if not plan:
        return None  # El plan no existe o está inactivo
    
    # 2. Buscamos que el usuario exista por su ID (datos.usuario_id)
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == datos.usuario_id).first()

    if not usuario:
        return None  # El usuario no existe

    # 3. Calculamos las fechas dinámicamente con la duración del plan
    fecha_inicio = datetime.now()
    fecha_fin = fecha_inicio + timedelta(days=plan.duracion)

    # 4. Guardamos la nueva membresía usando los datos calculados
    asignacion = membresiasModel(
        usuario_id=datos.usuario_id,
        plan_id=datos.plan_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
        # 'estado' no se pone porque la base de datos le asigna 'activa' por defecto
    )

    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)
    return asignacion


def membresia_usuario(db: Session, usuario_id: int):
    # Buscamos la membresía vigente ('activa') del usuario
    return db.query(membresiasModel).filter(
        membresiasModel.usuario_id == usuario_id,
        membresiasModel.estado == 'activa'
    ).first()
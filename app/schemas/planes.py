from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ==========================================
# 1. SCHEMAS PARA PLANES (Catálogo)
# ==========================================

# Clase Padre: Datos base que comparten las demás
class DatosPlan(BaseModel):
    tipo: str
    precio: float
    duracion: int

# Lo que DEVOLVEMOS al consultar planes (hereda datos base + suma id y estado)
class SalidaPlan(DatosPlan):
    id: int
    estado: str

    class Config:
        from_attributes = True


# ==========================================
# 2. SCHEMAS PARA MEMBRESÍAS DE USUARIO
# ==========================================

# Lo que RECIBIMOS cuando asignamos una membresía a un cliente
class AsignarMembresia(BaseModel):
    usuario_id: int
    plan_id: int

# Lo que DEVOLVEMOS como respuesta tras calcular la suscripción
class SalidaMembresia(BaseModel):
    id: int
    usuario_id: int
    plan_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: str
    creado_en: datetime

    class Config:
        from_attributes = True
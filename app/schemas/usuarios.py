# El datosUsuarios es el padre
#El entradaregistro se le suma el nombre y correo del padre,
#y la salida usuario quedaria con id,nombre y correo,
#La contraseña no porque entre hijas no se heredan
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic import Field


# 2. Datos base del usuario
class DatosUsuario(BaseModel):
    nombre: str
    correo: EmailStr

class EntradaLogin(BaseModel):
    correo: EmailStr
    password: str

# 3. Datos que entran en el Registro
class EntradaRegistro(DatosUsuario):
    password: str = Field(..., min_length=8, description="La contraseña debe tener al menos 8 caracteres")

# 4. Datos que salen en la respuesta (SalidaUsuario)
class SalidaUsuario(DatosUsuario):
    id: int
    rol_id: int
    rol: Optional[RolSalida] = None  # <--- le trae las columnas de la tabla rol o si sale algo mal por defecto le dara none

    class Config:
        from_attributes = True

# 5. Esquema para Actualizaciones
class ActualizarUsuario(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    password: Optional[str] = None

    class Config:
        from_attributes = True
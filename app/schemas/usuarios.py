# El datosUsuarios es el padre
#El entradaregistro se le suma el nombre y correo del padre,
#y la salida usuario quedaria con id,nombre y correo,
#La contraseña no porque entre hijas no se heredan
from typing import Optional
from pydantic import BaseModel, EmailStr

# 1. Los datos base que comparten las demás clases

class EntradaLogin(BaseModel):#Base model indnependiente
                             

    correo: EmailStr
    password: str


class DatosUsuario(BaseModel):
    nombre: str
    correo: EmailStr

# 2. Lo que RECIBIMOS cuando alguien llena el formulario de registro
class EntradaRegistro(DatosUsuario):
    password: str

# 3. Lo que DEVOLVEMOS como respuesta a la aplicación (Sin contraseña)
class SalidaUsuario(DatosUsuario):
    id: int

    class Config:
        from_attributes = True

# 4. Esquema exclusivo para actualizar (todos opcionales gracias a Optional)
class ActualizarUsuario(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    password: Optional[str] = None

    class Config:
        from_attributes = True

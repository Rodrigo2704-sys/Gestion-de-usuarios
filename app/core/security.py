# app/security.py
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt

# Importamos las variables ya validadas desde config.py
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Configuración de cifrado con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esa línea es el conector entre OpenAPI/Swagger y tu ruta de Login, y sirve para que FastAPI sepa cómo extraer el token de la cabecera HTTP de cada petición entrante.
autenticacion = OAuth2PasswordBearer(tokenUrl="/usuarios/login")


def hash_password(password: str):
    return pwd_context.hash(password)


def verificar_contraseña(contraseña_ingresada: str, password_hashed: str):
    return pwd_context.verify(contraseña_ingresada, password_hashed)


def crear_token_acceso(datos: dict, tiempo_expiracion: timedelta | None = None):
    datos_a_codificar = datos.copy()
    
    if tiempo_expiracion:
        expiracion = datetime.now(timezone.utc) + tiempo_expiracion
    else:
        expiracion = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    datos_a_codificar.update({"exp": expiracion})
    return jwt.encode(datos_a_codificar, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str = Depends(autenticacion)):
    try:
        contenido = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = contenido.get("sub")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Credenciales inválidas"
            )
            
        return email
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token inválido o expirado"
        )
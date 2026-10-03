# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

#  VALIDACIÓN CRÍTICA: Prohibido usar llaves por defecto en producción
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        " ERROR CRÍTICO DE SEGURIDAD: La variable de entorno 'SECRET_KEY' no está definida en el archivo .env"
    )

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Importamos el limiter desde su archivo limpio en core
from app.core.limiter import limiter

# Importamos los routers
from app.routers import usuarios
from app.routers import planes

app = FastAPI(
    title="Mi Backend Junior", 
    version="1.0.0",
    description="API desarrollada con FastAPI y SQLAlchemy con Arquitectura Limpia"
)

# Conectamos el limitador a la aplicación y su manejador de errores
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción recuerda acotarlo a tus dominios reales
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos y conectamos los routers
app.include_router(usuarios.router)
app.include_router(planes.router)

@app.get("/", tags=["Raíz"])
def read_root():
    return {"message": "¡Servidor corriendo al 100% con Rate Limiting modularizado!"}
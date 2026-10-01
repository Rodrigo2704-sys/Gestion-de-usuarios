# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import usuarios
from app.routers import planes  # <--- 1. IMPORTA TU NUEVO ROUTER DE PLANES

app = FastAPI(
    title="Mi Backend Junior", 
    version="1.0.0",
    description="API desarrollada con FastAPI y SQLAlchemy"
)

# Configuración de CORS (Esencial para conectar el backend con un frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambiar por los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectamos los routers
app.include_router(usuarios.router)
app.include_router(planes.router)  # <--- 2. REGISTRAR EL ROUTER EN LA APP

@app.get("/", tags=["Raíz"])
def read_root():
    return {"message": "¡Servidor corriendo al 100%!"}
from pydantic import BaseModel

class RolSalida(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

        #Sirve para que FastAPI pueda leer directamente los datos que vienen de la base de datos (SQLAlchemy) y convertirlos automáticamente en un JSON para responderle al cliente, sin que el sistema lance un error.

        #Sin esa línea: FastAPI espera un diccionario normal y falla si le entregas un objeto de base de datos.
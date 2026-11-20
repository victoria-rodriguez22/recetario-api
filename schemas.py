from pydantic import BaseModel

class ComidaCreate(BaseModel):
    nombre: str
    categoria: str
    dificultad: int
    precio: float

class ComidaResponse(ComidaCreate):
    id: int

    class Config:
        from_attributes = True
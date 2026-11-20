from sqlmodel import SQLModel, Field
from typing import Optional

class Comida(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    categoria: str  # Desayuno, Comida, Postre
    dificultad: int  # 1 a 10
    precio: float
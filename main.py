from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from database import engine, create_db_and_tables, get_session
from models import Comida
from schemas import ComidaCreate, ComidaResponse
from redis_cache import get_from_cache, set_to_cache, delete_from_cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Recetario API", lifespan=lifespan)

@app.post("/comidas/", response_model=ComidaResponse)
def crear_comida(comida: ComidaCreate, session: Session = Depends(get_session)):
    nueva = Comida.model_validate(comida)
    session.add(nueva)
    session.commit()
    session.refresh(nueva)
    delete_from_cache("comidas_lista")
    return nueva

@app.get("/comidas/", response_model=list[ComidaResponse])
def listar_comidas(session: Session = Depends(get_session)):
    clave = "comidas_lista"
    datos = get_from_cache(clave)
    if datos:
        return datos
    resultado = session.exec(select(Comida)).all()
    lista = [ComidaResponse.model_validate(c) for c in resultado]
    set_to_cache(clave, [c.model_dump() for c in lista])
    return lista

@app.get("/comidas/{comida_id}", response_model=ComidaResponse)
def obtener_comida(comida_id: int, session: Session = Depends(get_session)):
    clave = f"comida_{comida_id}"
    datos = get_from_cache(clave)
    if datos:
        return datos
    comida = session.get(Comida, comida_id)
    if not comida:
        raise HTTPException(status_code=404, detail="Comida no encontrada")
    respuesta = ComidaResponse.model_validate(comida)
    set_to_cache(clave, respuesta.model_dump())
    return respuesta

@app.put("/comidas/{comida_id}", response_model=ComidaResponse)
def actualizar_comida(comida_id: int, actualizar: ComidaCreate, session: Session = Depends(get_session)):
    comida = session.get(Comida, comida_id)
    if not comida:
        raise HTTPException(status_code=404, detail="Comida no encontrada")
    for campo, valor in actualizar.model_dump().items():
        setattr(comida, campo, valor)
    session.add(comida)
    session.commit()
    session.refresh(comida)
    delete_from_cache(f"comida_{comida_id}")
    delete_from_cache("comidas_lista")
    return comida

@app.delete("/comidas/{comida_id}")
def eliminar_comida(comida_id: int, session: Session = Depends(get_session)):
    comida = session.get(Comida, comida_id)
    if not comida:
        raise HTTPException(status_code=404, detail="Comida no encontrada")
    session.delete(comida)
    session.commit()
    delete_from_cache(f"comida_{comida_id}")
    delete_from_cache("comidas_lista")
    return {"mensaje": "Comida eliminada correctamente"}